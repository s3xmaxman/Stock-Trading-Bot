from django.db import models
from timescale.db.models.fields import TimescaleDateTimeField
from timescale.db.models.managers import TimescaleManager
from . import tasks

# Create your models here.


class Company(models.Model):
    """取引対象企業の情報を管理するモデル

    企業の基本情報、証券コード、アクティブステータスなどを管理します。
    新規作成時や更新時に自動的に株価データの同期タスクが実行されます。

    Attributes:
        name (str): 企業の正式名称（最大120文字）
        ticker (str): 証券コード（最大20文字、一意、インデックス付き、大文字に自動変換）
        description (str, optional): 企業の事業内容や特徴の説明
        active (bool): データ同期の有効/無効を示すフラグ（True: 有効, False: 無効）
        timestamp (datetime): レコード作成日時（自動設定）
        updated (datetime): 最終更新日時（自動更新）
    """

    name = models.CharField(max_length=120)
    ticker = models.CharField(max_length=20, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """レコード保存時の処理

        以下の処理を実行します：
        1. 証券コードを大文字に変換
        2. レコードを保存
        3. 非同期で株価データの同期タスクを実行

        Args:
            *args: 可変位置引数
            **kwargs: 可変キーワード引数
        """
        self.ticker = f"{self.ticker}".upper()
        super().save(*args, **kwargs)
        tasks.sync_company_stock_quotes.delay(self.pk)


class StockQuote(models.Model):
    """株価情報を管理するモデル

    1分間の取引データを保存し、TimescaleDBを使用して時系列データとして管理します。
    時系列データは1週間ごとにパーティション分割され、効率的なクエリを実現します。

    Attributes:
        company (Company): 対象企業（外部キー、CASCADE削除）
        open_price (Decimal): 始値（10桁、小数点以下4桁）
        close_price (Decimal): 終値（10桁、小数点以下4桁）
        high_price (Decimal): 高値（10桁、小数点以下4桁）
        low_price (Decimal): 安値（10桁、小数点以下4桁）
        number_of_trades (int): 取引回数（オプション）
        volume (int): 取引量（株数）
        volume_weighted_average (Decimal): 出来高加重平均価格（VWAP）（10桁、小数点以下6桁）
        raw_timestamp (str): APIから取得した生のタイムスタンプ（文字列、整数、浮動小数点）
        time (datetime): UTCタイムスタンプ（1週間間隔でパーティション）
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="stock_quotes",
    )
    open_price = models.DecimalField(max_digits=10, decimal_places=4)
    close_price = models.DecimalField(max_digits=10, decimal_places=4)
    high_price = models.DecimalField(max_digits=10, decimal_places=4)
    low_price = models.DecimalField(max_digits=10, decimal_places=4)
    number_of_trades = models.BigIntegerField(blank=True, null=True)
    volume = models.BigIntegerField()
    volume_weighted_average = models.DecimalField(max_digits=10, decimal_places=6)
    raw_timestamp = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        help_text="APIから取得した生のタイムスタンプ（文字列、整数、浮動小数点）",
    )
    time = TimescaleDateTimeField(interval="1 week")
    objects = models.Manager()
    timescale = TimescaleManager()

    class Meta:
        unique_together = [("company", "time")]
