"""Direct messages, private PDF attachments and public community media."""
from sqlalchemy import or_
from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, send_from_directory, url_for
from flask_login import current_user, login_required
from pathlib import Path

from .extensions import db
from .models import DirectMessage, MessageAttachment, User, utcnow
from .uploads import save_private_attachment, UploadError

messaging_bp = Blueprint("messaging", __name__)
media_bp = Blueprint("media", __name__)


@messaging_bp.get("/inbox")
@login_required
def inbox():
    messages = DirectMessage.query.filter(
        or_(DirectMessage.sender_id == current_user.id,
            DirectMessage.recipient_id == current_user.id)
    ).order_by(DirectMessage.created_at.desc()).limit(500).all()
    conversations = {}
    for item in messages:
        other_id = item.recipient_id if item.sender_id == current_user.id else item.sender_id
        if other_id not in conversations:
            other = db.session.get(User, other_id)
            if other:
                conversations[other_id] = {"member": other, "last_message": item, "unread": 0}
        if item.recipient_id == current_user.id and item.read_at is None and other_id in conversations:
            conversations[other_id]["unread"] += 1
    return render_template("messaging/inbox.html", conversations=list(conversations.values()))


@messaging_bp.route("/inbox/<int:member_id>", methods=["GET", "POST"])
@login_required
def conversation(member_id):
    if member_id == current_user.id:
        abort(400)
    member = db.get_or_404(User, member_id)
    if request.method == "POST":
        body = request.form.get("body", "").strip()[:3000]
        upload = request.files.get("attachment")
        has_file = bool(upload and upload.filename)
        if not body and not has_file:
            flash("Write a message or attach a photo / PDF document.", "error")
            return redirect(url_for("messaging.conversation", member_id=member_id))
        message = DirectMessage(sender_id=current_user.id, recipient_id=member_id, body=body)
        db.session.add(message)
        db.session.flush()
        if has_file:
            try:
                storage_name, original_name, size_bytes, mime_type = save_private_attachment(upload)
            except UploadError as exc:
                db.session.rollback()
                flash(str(exc), "error")
                return redirect(url_for("messaging.conversation", member_id=member_id))
            db.session.add(MessageAttachment(
                message_id=message.id, storage_name=storage_name,
                original_name=original_name, size_bytes=size_bytes, mime_type=mime_type,
            ))
        db.session.commit()
        flash("Message sent.", "success")
        return redirect(url_for("messaging.conversation", member_id=member_id))

    messages = DirectMessage.query.filter(
        or_(
            (DirectMessage.sender_id == current_user.id) & (DirectMessage.recipient_id == member_id),
            (DirectMessage.sender_id == member_id) & (DirectMessage.recipient_id == current_user.id),
        )
    ).order_by(DirectMessage.created_at.asc()).limit(300).all()
    changed = False
    for item in messages:
        if item.recipient_id == current_user.id and item.read_at is None:
            item.read_at = utcnow()
            changed = True
    if changed:
        db.session.commit()
    return render_template("messaging/conversation.html", member=member, messages=messages)


@messaging_bp.get("/private-media/<int:attachment_id>")
@login_required
def private_attachment(attachment_id):
    attachment = db.get_or_404(MessageAttachment, attachment_id)
    message = attachment.message
    if current_user.id not in {message.sender_id, message.recipient_id}:
        abort(404)
    root = Path(current_app.config["UPLOAD_FOLDER"])
    return send_from_directory(
        root, attachment.storage_name, as_attachment=not attachment.mime_type.startswith("image/"),
        download_name=attachment.original_name, mimetype=attachment.mime_type,
    )


@media_bp.get("/media/<path:storage_name>")
def public_media(storage_name):
    # Public media is limited to the public directory; private message files cannot be served here.
    if not storage_name.startswith("public/") or ".." in Path(storage_name).parts:
        abort(404)
    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"], storage_name,
        conditional=True, max_age=3600,
    )
