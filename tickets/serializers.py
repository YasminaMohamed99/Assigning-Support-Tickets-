from rest_framework import serializers
from .models import Ticket

class TicketSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ['created_by', 'assigned_to', 'assigned_at']

    def create(self, validated_data):
        user = self.context['request'].user
        if user.role != 'admin':
            raise serializers.ValidationError("Only admins can create tickets.")
        validated_data['created_by'] = user
        return super().create(validated_data)

    def get_created_by(self, obj):
        return {
            "id": obj.created_by.id,
            "username": obj.created_by.username,
        } if obj.created_by else None
