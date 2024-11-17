from rest_framework import serializers

from .models import gatepass


class gatepassserializer(serializers.ModelSerializer):
     class Meta:
          model = gatepass
          fields = '__all__' 