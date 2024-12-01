import os
import sys
import pathlib

# このファイルのパスを解決する
THIS_FILE_PATH = pathlib.Path(__file__).resolve()
# ノートブックディレクトリ
NBS_DIR = THIS_FILE_PATH.parent
# リポジトリのルートディレクトリ
REPO_DIR = NBS_DIR.parent
# Djangoプロジェクトのベースディレクトリ
DJANGO_BASE_DIR = REPO_DIR / "src"


def init_django(project_name="trading"):
    """
    Djangoの管理タスクを実行するための初期化を行う。

    Args:
        project_name (str): Djangoプロジェクト名。デフォルトは"trading"。

    この関数は以下の操作を行います：
    1. 作業ディレクトリをDjangoのベースディレクトリに変更
    2. Djangoプロジェクトのパスをシステムパスに追加
    3. Django設定モジュールを環境変数に設定
    4. 非同期操作を許可する環境変数を設定
    5. Djangoをセットアップ
    """
    # Djangoプロジェクトのディレクトリに移動
    os.chdir(DJANGO_BASE_DIR)
    # Djangoプロジェクトのパスをシステムパスに追加
    sys.path.insert(0, str(DJANGO_BASE_DIR))
    # Django設定モジュールを環境変数に設定
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"{project_name}.settings")
    # 非同期操作を許可する環境変数を設定
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    # Djangoをインポートしてセットアップ
    import django

    django.setup()
