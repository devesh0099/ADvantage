from BidRequest import BidRequest

class Bidder():

    def getBidPrice(self, bidRequest: BidRequest) -> int:
        pass

    def preProcessInput(self, BidRequest: BidRequest):
        pass
    
    def getPredictedPrice(self, BidRequest:BidRequest)->int:
        pass

    def getScoreDelta(self, BidRequest: BidRequest) -> float:
        pass
