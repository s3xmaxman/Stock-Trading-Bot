from django.apps import apps


def batch_insert_stock_data(
    dataset,
    company_obj=None,
    batch_size=1000,
    verbose=False,
):
    """株価データを一括でデータベースに挿入する関数

    Args:
        dataset (list): 挿入する株価データのリスト
        company_obj (Company): 会社オブジェクト。デフォルトはNone
        batch_size (int): 一度に挿入するデータの数。デフォルトは1000
        verbose (bool): 詳細なログを出力するかどうか。デフォルトはFalse

    Returns:
        int: 挿入されたデータの総数

    Raises:
        Exception: company_objが無効な場合に発生
    """
    # StockQuoteモデルを動的にインポート
    StockQuote = apps.get_model("market", "StockQuote")
    batch_size = 1000

    # 会社オブジェクトの検証
    if company_obj is None:
        raise Exception(f"Batch failed. Company Object {company_obj} invalid")

    # データセットをバッチサイズごとに処理
    for i in range(0, len(dataset), batch_size):
        if verbose:
            print("Doing chunk", i)

        # 現在のバッチのデータを取得
        batch_chunk = dataset[i : i + batch_size]
        chunked_quotes = []

        # 各データをStockQuoteオブジェクトに変換
        for data in batch_chunk:
            chunked_quotes.append(StockQuote(company=company_obj, **data))

        # バッチ単位でデータベースに一括挿入
        StockQuote.objects.bulk_create(chunked_quotes, ignore_conflicts=True)

        if verbose:
            print("finished chunk", i)

    return len(dataset)
