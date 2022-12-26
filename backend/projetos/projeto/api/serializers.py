from rest_framework import serializers

from projetos.projeto.models import Projeto


class ProjetoListSerializer(serializers.ModelSerializer):
    unidades_count = serializers.IntegerField(
                        source='unidades.count', 
                        read_only=True
                        )
    ativos_count = serializers.ReadOnlyField(
        source='count_assets'
                        )

    porcentage = serializers.ReadOnlyField(
        source='porcentage_complete'
                        )

    #porc_complete = serializers.SerializerMethodField()
    
    class Meta:
        model = Projeto
        fields = "__all__"
    
    # def get_porc_complete(self, instance):
    #     return 1
    #     #return instance.unidades.count


class ProjetoDetailSerializer(serializers.ModelSerializer):
    
    porcentage = serializers.ReadOnlyField(
        source='porcentage_complete'
                        )

    class Meta:
        model = Projeto
        fields = "__all__"


