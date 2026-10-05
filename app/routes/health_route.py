from flask import Blueprint


bp = Blueprint("health", __name__, url_prefix="/api/v1/health")


@bp.route("", methods=["GET"])
def health():
    return {
        "status": "ok"
    }, 200