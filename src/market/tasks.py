from celery import shared_task
from datetime import timedelta

from django.apps import apps
from django.utils import timezone

import helpers.clients as helper_clients

from .utils import batch_insert_stock_data


@shared_task
def sync_company_stock_quotes(
    company_id, days_ago=32, date_format="%Y-%m-%d", verbose=False
):
    """特定の企業の株価データを同期するタスク

    Args:
        company_id (int): 企業のID
        days_ago (int, optional): 何日前からのデータを取得するか. デフォルトは32日前
        date_format (str, optional): 日付のフォーマット. デフォルトは"%Y-%m-%d"
        verbose (bool, optional): 詳細なログを出力するかどうか. デフォルトはFalse

    Raises:
        Exception: 企業IDが無効な場合、または企業のティッカーシンボルが無効な場合
    """
    Company = apps.get_model("market", "Company")
    try:
        company_obj = Company.objects.get(id=company_id)
    except:
        company_obj = None
    if company_obj is None:
        raise Exception(f"Company Id {company_id} invalid")
    company_ticker = company_obj.ticker
    if company_ticker is None:
        raise Exception(f"{company_ticker} invalid")

    # 日付範囲の計算
    now = timezone.now()
    start_date = now - timedelta(days=days_ago)
    to_date = start_date + timedelta(days=days_ago + 1)
    to_date = to_date.strftime(date_format)
    from_date = start_date.strftime(date_format)

    # Polygon APIクライアントを初期化し、株価データを取得
    client = helper_clients.PolygonAPIClient(
        ticker=company_ticker, from_date=from_date, to_date=to_date
    )
    dataset = client.get_stock_data()
    if verbose:
        print("dataset length", len(dataset))
    batch_insert_stock_data(dataset=dataset, company_obj=company_obj, verbose=verbose)


@shared_task
def sync_stock_data(days_ago=2):
    """アクティブな全企業の株価データを同期するタスク

    Args:
        days_ago (int, optional): 何日前からのデータを取得するか. デフォルトは2日前
    """
    Company = apps.get_model("market", "Company")
    # アクティブな企業のIDリストを取得
    companies = Company.objects.filter(active=True).values_list("id", flat=True)
    for company_id in companies:
        sync_company_stock_quotes.delay(company_id, days_ago=days_ago)


@shared_task
def sync_historical_stock_data(
    years_ago=5,
    company_ids=[],
    use_celery=True,
    verbose=False,
):
    """企業の過去の株価データを同期するタスク

    指定された年数分の過去データを30日ごとのバッチで取得します.
    大量のデータを扱うため、Celeryを使用して非同期で処理することができます.

    Args:
        years_ago (int, optional): 何年前までのデータを取得するか. デフォルトは5年前
        company_ids (list, optional): 特定の企業IDのリスト. 空リストの場合は全アクティブ企業が対象
        use_celery (bool, optional): Celeryを使用して非同期処理を行うかどうか. デフォルトはTrue
        verbose (bool, optional): 詳細なログを出力するかどうか. デフォルトはFalse
    """
    Company = apps.get_model("market", "Company")
    qs = Company.objects.filter(active=True)
    if len(company_ids) > 0:
        qs = qs.filter(id__in=company_ids)
    companies = qs.values_list("id", flat=True)

    # 各企業に対して、指定された年数分のデータを30日ごとのバッチで処理
    for company_id in companies:
        days_starting_ago = 30 * 12 * years_ago  # 年数を日数に変換
        batch_size = 30  # 30日ごとにバッチ処理
        for i in range(30, days_starting_ago, batch_size):
            if verbose:
                print("Historical sync days ago", i)
            if use_celery:
                sync_company_stock_quotes.delay(company_id, days_ago=i, verbose=verbose)
            else:
                sync_company_stock_quotes(company_id, days_ago=i, verbose=verbose)
            if verbose:
                print(i, "done\n")
