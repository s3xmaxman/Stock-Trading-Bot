import zoneinfo
from django.contrib import admin
from django.utils import timezone
from rangefilter.filters import (
    DateTimeRangeFilterBuilder,
)

# Register your models here.
from .models import StockQuote, Company

admin.site.register(Company)


class StockQuoteAdmin(admin.ModelAdmin):
    """株価データの管理画面のカスタマイズクラス

    株価データの表示、フィルタリング、ソートなどの機能を提供します。
    タイムゾーンはUTCで保存され、表示時にUS/Easternに変換されます。
    """

    list_display = ["company", "localized_time", "open_price", "close_price", "volume"]
    list_filter = [
        ("time", DateTimeRangeFilterBuilder()),
        "company",
    ]

    def get_queryset(self, request):
        """クエリセットを取得し、タイムゾーンを設定するメソッド

        Args:
            request: HTTPリクエストオブジェクト

        Returns:
            QuerySet: タイムゾーンが設定された株価データのクエリセット
        """
        tz_name = "US/Eastern"
        tz_name = "UTC"
        user_tz = zoneinfo.ZoneInfo(tz_name)
        timezone.activate(user_tz)
        return super().get_queryset(request)

    def localized_time(self, obj):
        """株価データの時刻をUS/Easternタイムゾーンに変換して表示するメソッド

        Args:
            obj: StockQuoteオブジェクト

        Returns:
            str: フォーマットされた現地時刻文字列（例: "Dec 01, 2024, 09:30 AM (EST)"）
        """
        tz_name = "US/Eastern"
        user_tz = zoneinfo.ZoneInfo(tz_name)
        local_time = obj.time.astimezone(user_tz)
        return local_time.strftime("%b %d, %Y, %I:%M %p (%Z)")


admin.site.register(StockQuote, StockQuoteAdmin)
