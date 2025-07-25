import pandas as pd
from typing import Dict, Any
from BidRequest import BidRequest
from ADvantage.Bid import Bid

columnNames = [
    "BidId", "Timestamp", "VisitorID", "User-Agent", "IP", "Region", "City",
    "Ad-Exchange", "Domain", "URL", "AnonymousURLID", "AdSlotID", "AdSlotWidth",
    "AdSlotHeight", "AdSlotVisibility", "AdSlotFormat", "AdSlotFloorPrice",
    "CreativeID", "BiddingPrice", "AdvertiserID", "Person-Tags"
]

def process_bid_requests(input_file: str, output_file: str):
    bidder = Bid()
    
    with open(output_file, 'w') as out:
        if input_file.endswith('.txt'):
            
            df = pd.read_csv(
                input_file,
                sep="\t",
                header=None,
                names=columnNames,
                index_col=False
            )
            for _, row in df.iterrows():
                process_row(row.to_dict(), bidder, out)
        else:
            print("Error txt file is not provided.")

def process_row(data: Dict[str, Any], bidder: Bid, out_file):
    request = BidRequest()

    key_mapping = {
        "BidId": "bidId",
        "Timestamp": "timestamp",
        "VisitorID": "visitorId",
        "User-Agent": "userAgent",
        "IP": "ipAddress",
        "Region": "region",
        "City": "city",
        "Ad-Exchange": "adExchange",
        "Domain": "domain",
        "URL": "url",
        "AnonymousURLID": "anonymousURLID",
        "AdSlotID": "adSlotID",
        "AdSlotWidth": "adSlotWidth",
        "AdSlotHeight": "adSlotHeight",
        "AdSlotVisibility": "adSlotVisibility",
        "AdSlotFormat": "adSlotFormat",
        "AdSlotFloorPrice": "adSlotFloorPrice",
        "CreativeID": "creativeID",
        "BiddingPrice": "biddingPrice",
        "AdvertiserID": "advertiserId",
        "Person-Tags": "userTags"
    }

    for key, value in data.items():
        mapped_key = key_mapping.get(key)
        if mapped_key is None:
            continue

        if pd.isna(value) or str(value).strip().lower() == 'null':
            value = None
        else:
            value = str(value).strip()
        setattr(request, mapped_key, value)
    bid_price = bidder.getBidPrice(request)
    result = f"{request.bidId}\t{bid_price}\n"
    out_file.write(result)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python process_bids.py <input_file> <output_file>")
        sys.exit(1)
        
    process_bid_requests(sys.argv[1], sys.argv[2])
