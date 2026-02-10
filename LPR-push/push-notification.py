import argparse
import base64
import logging
import os
import socket
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Tuple

from flask import Flask, jsonify, request
from werkzeug.serving import make_server


DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8080

flask_app = Flask(__name__)
logger = logging.getLogger("lpr-push")
server_config = {"image_dir": Path.home() / "tollgate_images"}


def get_server_ip() -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        sock.close()


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(message)s",
    )
    logging.getLogger("werkzeug").setLevel(logging.WARNING)


def ensure_output_dir(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def save_image(data: Dict[str, Any]) -> Tuple[Path, str]:
    picture = data["Picture"]["NormalPic"]
    file_name = picture.get("PicName", f"image_{datetime.now():%Y%m%d_%H%M%S}.jpg")
    file_name = os.path.basename(file_name)

    image_bytes = base64.b64decode(picture["Content"])
    destination = server_config["image_dir"] / file_name
    destination.write_bytes(image_bytes)

    plate_number = data.get("Picture", {}).get("Plate", {}).get("PlateNumber", "Unknown")
    return destination, plate_number


@flask_app.route("/health", methods=["GET"])
def health() -> Tuple[Dict[str, str], int]:
    return {"status": "ok"}, 200


@flask_app.route("/NotificationInfo/<action>", methods=["POST"])
def handle_notification(action: str):
    try:
        if not request.is_json:
            logger.warning("Payload without JSON from %s", request.remote_addr)
            return jsonify({"Result": True}), 200

        notification_data = request.get_json(silent=True) or {}
        normal_picture = notification_data.get("Picture", {}).get("NormalPic", {})

        if not normal_picture.get("Content"):
            logger.warning(
                "Notification without image. action=%s ip=%s",
                action,
                request.remote_addr,
            )
            return jsonify({"Result": True}), 200

        image_path, plate_number = save_image(notification_data)
        logger.info(
            "Notification processed. action=%s ip=%s plate=%s file=%s",
            action,
            request.remote_addr,
            plate_number,
            image_path,
        )
    except Exception as exc:
        logger.exception("Failed to process notification: %s", exc)

    return jsonify({"Result": True}), 200


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="LPR Push server without GUI (Linux compatible)",
    )
    parser.add_argument("--host", default=DEFAULT_HOST, help="Server bind host")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Server port")
    parser.add_argument(
        "--output-dir",
        default=os.getenv("LPR_PUSH_OUTPUT_DIR", str(Path.home() / "tollgate_images")),
        help="Directory used to store received images",
    )
    parser.add_argument(
        "--log-level",
        default=os.getenv("LPR_PUSH_LOG_LEVEL", "INFO"),
        help="Log level (DEBUG, INFO, WARNING, ERROR)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    configure_logging(args.log_level)

    output_dir = ensure_output_dir(Path(args.output_dir).expanduser())
    server_config["image_dir"] = output_dir

    logger.info("Server starting at http://%s:%s", args.host, args.port)
    logger.info("Detected local IP: %s", get_server_ip())
    logger.info("Image directory: %s", output_dir)

    server = make_server(args.host, args.port, flask_app)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()