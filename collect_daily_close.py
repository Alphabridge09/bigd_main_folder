"""
장마감 직후 하루 1회 실행되는 스크립트.
관심종목(watchlist.csv)의 그날 최종 종가를 네이버 API로 조회해 Turso DB의 price_history
테이블에 누적 저장한다 (종목별 최근 15거래일치만 유지, 오래된 행은 삭제).

여기서 쌓은 종가를 실제로 읽어 그래프에 그리는 것은 다음 주에 한다 — 이번 주는 "쌓기"까지다.

예전에는 price_history.json 파일을 저장소에 직접 커밋해 상태를 유지했지만, DB 자체가 영속
저장소이므로 이제 그럴 필요가 없다.

⚠️ read_watchlist()와 fetch_naver_current_price()는 notify_stock_price.py에도 **똑같은 것이
한 벌 더** 들어 있다. 두 스크립트가 같은 일(관심종목 읽기, 현재가 조회)을 해야 하는데 각자
자기 파일 안에 갖고 있어서 그렇다. 한쪽을 고치면 다른 쪽도 똑같이 고쳐야 한다.
"""

from datetime import datetime
from stock_utils import (
    KST,
    read_watchlist,
    update_price_history,
    fetch_naver_current_price,
    get_turso_client,
)
watchlist_codes = read_watchlist()

if watchlist_codes is None:
    exit()
print(f"🚀 종가 수집 시작... (실행 시각 {datetime.now(KST).strftime('%Y-%m-%d %H:%M')} KST)")
collected = 0
with get_turso_client() as client:
    for code in watchlist_codes:
        info = fetch_naver_current_price(code)
        if info is None:
            continue
        if info["is_open"]:
            print(f"⚠️⚠️ [{code}] 아직 장중입니다. 확정되지 않은 가격이라 기록하지 않습니다.")
            continue
        traded_at = info.get("traded_at") or ""
        if len(traded_at) >= 10:
            date_str = traded_at[:10].replace("-", "")
        else:
            date_str = datetime.now(KST).strftime("%Y%m%d")
            print(f"⚠️⚠️ [{code}] 체결 시각을 읽지 못해 실행 시각 기준으로 날짜를 정합니다.")
        update_price_history(code, date_str, info["price"], client=client)
        collected += 1
        print(f"✅ [{code}] {info['name']} {date_str} 종가 {info['price']:,}원 기록")
if collected == 0:
    print("❌ 기록된 종가가 하나도 없습니다.")
    exit()
print(f"🎉 종가 히스토리를 Turso DB에 저장했습니다 ({collected}/{len(watchlist_codes)}종목).")