from azure.identity import DefaultAzureCredential
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.authorization.models import RoleAssignmentCreateParameters
import requests
import uuid

def get_user_object_id(user_principal_name, credential):
    token = credential.get_token("https://graph.microsoft.com/.default").token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.get(
        f"https://graph.microsoft.com/v1.0/users/{user_principal_name}",
        headers=headers
    )
    response.raise_for_status()
    user_data = response.json()
    return user_data['id']

def assign_role_to_user():
    # Get user input
    user_principal_name = input("Enter the user principal name (email): ")
    role_definition_name = input("Enter the role definition name (e.g., Contributor, Reader): ")
    subscription_id = input("Enter the subscription ID: ")
    description = input("Enter the description: ")


    # Authenticate using DefaultAzureCredential
    credential = DefaultAzureCredential()
    client = AuthorizationManagementClient(credential, subscription_id)

    # Get the user object ID
    try:
        user_object_id = get_user_object_id(user_principal_name, credential)
    except Exception as e:
        print(f"Failed to get user object ID: {e}")
        return

    # Get the role definition ID
    role_definitions = client.role_definitions.list(
        scope=f"/subscriptions/{subscription_id}",
        filter=f"roleName eq '{role_definition_name}'"
    )
    role_definition_id = None
    for role_definition in role_definitions:
        role_definition_id = role_definition.id
        break

    if not role_definition_id:
        print(f"Role '{role_definition_name}' not found.")
        return

    # Create role assignment
    role_assignment_id = str(uuid.uuid4())
    scope = f"/subscriptions/{subscription_id}"
    role_assignment_params = RoleAssignmentCreateParameters(
        role_definition_id=role_definition_id,
        principal_id=user_object_id,
        description=description
    )

    try:
        role_assignment = client.role_assignments.create(
            scope=scope,
            role_assignment_name=role_assignment_id,
            parameters=role_assignment_params
        
        )
        print(f"Role '{role_definition_name}' assigned to '{user_principal_name}' successfully.")
    except Exception as e:
        print(f"Failed to assign role: {e}")

if __name__ == "__main__":
    assign_role_to_user()