from rest_framework import serializers 
from .models import Modelfactors 
from .models import Intradaymarketdata

class FactorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Modelfactors 
        fields = '__all__'


class PriceSeriesSerializer(serializers.ModelSerializer):
    #serializer acting on the market data model and returning an array of instances of {time, price}
    class Meta:
        model = Intradaymarketdata
        fields = ['dt', 'trade'] 


