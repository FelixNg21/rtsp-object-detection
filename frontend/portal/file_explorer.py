import os
from flask import Flask, send_from_directory, Blueprint, request, render_template, current_app

bp = Blueprint('file_explorer', __name__, url_prefix='/file_explorer')


@bp.route('/files', defaults={'subpath': ''}, methods=['GET'])
@bp.route('/files/<path:subpath>', methods=['GET'])
def list_files(subpath):
    base_dir = current_app.config['FILE_DIRECTORY']
    abs_path = os.path.join(base_dir, subpath)
    files = []
    dirs = []
    if request.method == 'GET':
        for entry in os.listdir(abs_path):
            if os.path.isdir(os.path.join(abs_path, entry)):
                dirs.append(entry)
            else:
                files.append(entry)

    path_parts = subpath.split('/') if subpath else []
    cumulative_paths = ["/".join(path_parts[:i + 1]) for i in range(len(path_parts))]

    return render_template('file_explorer/files.html', files=files, dirs=dirs, subpath=subpath,
                           path_parts=path_parts, cumulative_paths=cumulative_paths)


@bp.route('/download/<path:subpath>/<path:filename>', methods=['GET'])
def download_file(subpath, filename):
    return send_from_directory(os.path.join(current_app.config['FILE_DIRECTORY'], subpath), filename, as_attachment=True)
    # return send_from_directory(current_app.config['FILE_DIRECTORY'], filename, as_attachment=True)

@bp.route('/play/<path:subpath>/<path:filename>', methods=['GET'])
def serve_video(subpath, filename):
    return send_from_directory(os.path.join(current_app.config['FILE_DIRECTORY'], subpath), filename, as_attachment=False)

