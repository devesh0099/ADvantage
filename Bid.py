from BidRequest import BidRequest
from Bidder import Bidder
import onnxruntime as ort
import numpy as np
import pickle
import helper.PredictedScoreDelta as Generator
from helper.PredictedScoreDelta import encoder_mapping

class Bid(Bidder):
    _model = None
    _encoders = None

    def __init__(self):
        if Bid._model is None:
            Bid._model = ort.InferenceSession("model/lightgbm_model.onnx")
        self.model = Bid._model

        if Bid._encoders is None:
            with open("model/label_encoders.pkl", "rb") as f:
                Bid._encoders = pickle.load(f)
        self.encoders = Bid._encoders
        

    def preProcessInput(self, BidRequest: BidRequest):
        
        composite_key = f"{str(BidRequest.creativeID)}_{str(BidRequest.advertiserId)}"
        
        encoder_dict = {}
        
        encoder_dict["CompositeKey"] = self.encoders["CompositeKey"].transform([composite_key])[0]
        encoder_dict["AdSlotID"] = encoder_mapping.get(BidRequest.adSlotID, -1)
        
        input_features = {
            "CompositeKey":encoder_dict["CompositeKey"],
            "AdSlotID":encoder_dict["AdSlotID"],
            "AdSlotFormat":BidRequest.adSlotFormat,
            "Region":BidRequest.region,
            "AdSlotVisibility":BidRequest.adSlotVisibility,
            "Ad-Exchange":BidRequest.adExchange
        }
        
        return np.array([
            input_features["CompositeKey"],
            input_features["AdSlotID"],
            input_features["AdSlotFormat"],
            input_features["Region"],
            input_features["AdSlotVisibility"],
            input_features["Ad-Exchange"]
        ], dtype=np.float32).reshape(1, -1)
    
    def getPredictedPrice(self, BidRequest:BidRequest)->int:
        
        processed_input = self.preProcessInput(BidRequest)
        
        prediction = self.model.run(None, {"input": processed_input})
        
        return int(prediction[0][0])

    def getScoreDelta(self, BidRequest: BidRequest) -> float:
        return Generator.scoreDeltaGenerator(BidRequest)
    
    def getBidPrice(self, BidRequest: BidRequest) -> int:
        predictedPrice = float(self.getPredictedPrice(BidRequest))
        scoreDelta = float(self.getScoreDelta(BidRequest))
        

        bidPrice = -1
        if(scoreDelta > 0.0055 and scoreDelta < 0.0065):
            return -1
        elif(scoreDelta <= 0.0055):
            bidPrice = (predictedPrice+20) + predictedPrice*0.2
        else:
            bidPrice = (predictedPrice+20) + predictedPrice*0.4
        
        # Checking AdSlotFloorPrice and Absurd high BidPrice
        if(bidPrice <= int(BidRequest.getAdSlotFloorPrice()) or bidPrice >=350):
          return -1
        return bidPrice
        
        
    
