# import strawberry
# from timbre.models import TypeTimbre
# from timbre.types import Message, TypeTimbreType
# from users.models import User

# @strawberry.type
# class TimbreTypeMutation:
#     @strawberry.mutation()
#     def add_timre_type(self,name:str) -> TypeTimbreType:
#         timbre_type = TypeTimbre.objects.create(name = name,created_by=User.objects.get(pk=1),updated_by=User.objects.get(pk=1))
#         return timbre_type
    
#     @strawberry.mutation()
#     def change_timre_type_name(self,id:int,name:str) -> TypeTimbreType:
#         timbre_type = TypeTimbre.objects.get(pk=id)
#         timbre_type.updated_by=User.objects.get(pk=1)
#         timbre_type.save()
#         return timbre_type

#     @strawberry.mutation()
#     def delete_type_timbre(self,id:int) -> Message:
#         try:
#             typeTimbre = TypeTimbre.objects.get(pk=id)
#             typeTimbre.delete()
#             return Message(success=True,message="Type timbre deleted")
#         except TypeTimbre.DoesNotExist:
#             return Message(success=False,message="Type timbre not found")