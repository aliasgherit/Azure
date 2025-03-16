from azure.identity import DefaultAzureCredential
from azure.mgmt.authorization import AuthorizationManagementClient
import requests

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

def remove_role_from_user():
    # Get user input
    user_principal_name = input("Enter the user principal name (email): ")
    role_definition_name = input("Enter the role definition name (e.g., Contributor, Reader): ")
    subscription_id = input("Enter the subscription ID: ")

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

    # Find the role assignment
    role_assignments = client.role_assignments.list_for_scope(
        scope=f"/subscriptions/{subscription_id}",
        filter=f"principalId eq '{user_object_id}'"
    )
    role_assignment_id = None
    for role_assignment in role_assignments:
        if role_assignment.role_definition_id == role_definition_id:
            role_assignment_id = role_assignment.name
            break

    if not role_assignment_id:
        print(f"No role assignment found for user '{user_principal_name}' with role '{role_definition_name}'.")
        return

    # Remove role assignment
    try:
        client.role_assignments.delete(
            scope=f"/subscriptions/{subscription_id}",
            role_assignment_name=role_assignment_id
        )
        print(f"Role '{role_definition_name}' removed from '{user_principal_name}' successfully.")
    except Exception as e:
        print(f"Failed to remove role: {e}")

if __name__ == "__main__":
    remove_role_from_user()