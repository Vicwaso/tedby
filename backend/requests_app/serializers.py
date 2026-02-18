from rest_framework import serializers

class InitRequestSerializer(serializers.Serializer):
    idNumber = serializers.CharField(max_length=10)
    firstName = serializers.CharField(max_length=60)
