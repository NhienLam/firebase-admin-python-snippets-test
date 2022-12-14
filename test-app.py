import firebase_admin
from firebase_admin import credentials
from firebase_admin import tenant_mgt
from firebase_admin import auth
from firebase_admin import exceptions

# In Firebase Console > Project settings > Service accounts > Generate new private key
# Put the path to your generated service account key here
PATH_TO_SERVICE_ACCOUNT_KEY = ''
CREDENTIAL = credentials.Certificate(PATH_TO_SERVICE_ACCOUNT_KEY)
default_app = firebase_admin.initialize_app(CREDENTIAL)

##### https://cloud.google.com/identity-platform/docs/multi-tenancy-managing-tenants #####
### Tenant management ###
## getTenantClient()
def get_tenant_client(tenant_id):
  tenant_client = tenant_mgt.auth_for_tenant(tenant_id)
  return tenant_client


## Getting an existing tenant
def get_tenant(tenant_id):
  tenant = tenant_mgt.get_tenant(tenant_id)
  print('Retreieved tenant:', tenant.tenant_id)


## Creating a tenant
def create_tenant():
  tenant = tenant_mgt.create_tenant(
      display_name='tenant-test-1',
      enable_email_link_sign_in=True,
      allow_password_sign_up=True,
  )

  print('Created tenant:', tenant.tenant_id)


## Updating a tenant
def update_tenant(tenant_id):
  tenant = tenant_mgt.update_tenant(
      tenant_id, display_name='updatedName', allow_password_sign_up=False
  )  # Disable email provider

  print('Updated tenant:', tenant.tenant_id)


## Deleting a tenant
def delete_tenant(tenant_id):
  tenant_mgt.delete_tenant(tenant_id)


## Listing tenants
def list_tenants():
  for tenant in tenant_mgt.list_tenants().iterate_all():
    print('Retrieved tenant:', tenant.tenant_id)


### Managing SAML and OIDC providers programmatically ###
## Creating a provider
def create_provider_tenant(tenant_client):
  saml = tenant_client.create_saml_provider_config(
      display_name='SAML provider name',
      enabled=True,
      provider_id='saml.myProvider',
      idp_entity_id='IDP_ENTITY_ID',
      sso_url='https://example.com/saml/sso/1234/',
      x509_certificates=[
          '-----BEGIN CERTIFICATE-----\nCERT1...\n-----END CERTIFICATE-----',
          '-----BEGIN CERTIFICATE-----\nCERT2...\n-----END CERTIFICATE-----',
      ],
      rp_entity_id='P_ENTITY_ID',
      callback_url='https://project-id.firebaseapp.com/__/auth/handler',
  )

  print('Created new SAML provider:', saml.provider_id)


## Modifying a provider
def update_provider_tenant(tenant_client):
  saml = tenant_client.update_saml_provider_config(
      'saml.myProvider',
      x509_certificates=[
          '-----BEGIN CERTIFICATE-----\nCERT2...\n-----END CERTIFICATE-----',
          '-----BEGIN CERTIFICATE-----\nCERT3...\n-----END CERTIFICATE-----',
      ],
  )

  print('Updated SAML provider:', saml.provider_id)


## Getting a provider
def get_provider_tenant(tennat_client):
  saml = tennat_client.get_saml_provider_config('saml.myProvider')
  print(saml.display_name, saml.enabled)


## Listing providers
def list_provider_configs_tenant(tenant_client):
  for saml in tenant_client.list_saml_provider_configs(None).iterate_all():
    print(saml.provider_id)


## Deleting a provider
def delete_provider_config_tenant(tenant_client):
  tenant_client.delete_saml_provider_config('saml.myProvider')


### Managing tenant specific users ###
##Getting a user
def get_user_tenant(tenant_client):
  user = tenant_client.get_user(uid)
  print('Successfully fetched user data:', user.uid)


## You can also identify a user by their email
def get_user_by_email_tenant(tenant_client):
  email = 'user@example.com'
  user = tenant_client.get_user_by_email(email)
  print('Successfully fetched user data:', user.uid)


## Creating a user
def create_user_tenant(tenant_client):
  user = tenant_client.create_user(
      email='user123@example.com',
      email_verified=False,
      phone_number='+15551550100',
      password='secretPassword',
      display_name='John Doe',
      photo_url='http://www.example.com/12345678/photo.png',
      disabled=False,
  )
  print('Sucessfully created new user:', user.uid)


## Modifying a user
def update_user_tenant(tenant_client, uid):
  user = tenant_client.update_user(
      uid,
      email='user123@example.com',
      phone_number='+15555550123',
      email_verified=True,
      password='newPassword',
      display_name='John Doe',
      photo_url='http://www.example.com/12345678/photo.png',
      disabled=True,
  )
  print('Sucessfully updated user:', user.uid)


## Deleting a user
def delete_user_tenant(tenant_client, uid):
  tenant_client.delete_user(uid)
  print('Successfully deleted user')


## Listing users
def list_users_tenant(tenant_client):
  for user in tenant_client.list_users().iterate_all():
    print('User: ' + user.uid)

    # Iterating by pages of 1000 users at a time.
  page = tenant_client.list_users()
  while page:
    for user in page.users:
      print('User: ' + user.uid)
    # Get next batch of users.
    page = page.get_next_page()


### Importing users
def import_with_hmac_tenant(tenant_client):
  users = [
      auth.ImportUserRecord(
          uid='uid1',
          email='user1@example.com',
          password_hash=b'password_hash_1',
          password_salt=b'salt1',
      ),
      auth.ImportUserRecord(
          uid='uid2',
          email='user2@example.com',
          password_hash=b'password_hash_2',
          password_salt=b'salt2',
      ),
  ]

  hash_alg = auth.UserImportHash.hmac_sha256(key=b'secret')
  try:
    result = tenant_client.import_users(users, hash_alg=hash_alg)
    for err in result.errors:
      print('Failed to import user:', err.reason)
  except exceptions.FirebaseError as error:
    print('Error importing users:', error)


## Users without passwords can also be imported to a specific tenant.
def import_without_password_tenant(tenant_client):
  users = [
      auth.ImportUserRecord(
          uid='some-uid',
          display_name='John Doe',
          email='johndoe@gmail.com',
          photo_url='http://www.example.com/12345678/photo.png',
          email_verified=True,
          phone_number='+11234567890',
          custom_claims={'admin': True},  # set this user as admin
          provider_data=[  # user with SAML provider
              auth.UserProvider(
                  uid='saml-uid',
                  email='johndoe@gmail.com',
                  display_name='John Doe',
                  photo_url='http://www.example.com/12345678/photo.png',
                  provider_id='saml.acme',
              )
          ],
      ),
  ]
  try:
    result = tenant_client.import_users(users)
    for err in result.errors:
      print('Failed to import user:', err.reason)
  except exceptions.FirebaseError as error:
    print('Error importing users:', error)


### Identity verification ###
def verify_id_token_tenant(tenant_client, id_token):
  try:
    decoded_token = tenant_client.verify_id_token(id_token)

    # This should be set to TENANT-ID. Otherwise TenantIdMismatchError error raised.
    print('Verified ID token from tenant:', decoded_token['firebase']['tenant'])
  except tenant_mgt.TenantIdMismatchError:
    # Token revoked, inform the user to reauthenticate or signOut().
    print('error')
    pass


### Managing user sessions ###
# The refresh tokens can then be revoked by specifying the uid of that user
def revoke_refresh_tokens_tenant(tenant_client, uid):
  tenant_client.revoke_refresh_tokens(uid)

  user = tenant_client.get_user(uid)
  # Convert to seconds as the auth_time in the token claims is in seconds.
  revocation_second = user.tokens_valid_after_timestamp / 1000
  print('Tokens revoked at: {0}'.format(revocation_second))


## You can verify that an unexpired valid ID token is not revoked by specifying the optional checkRevoked parameter; this checks if a token is revoked after its integrity and authenticity is verified.
def verify_id_token_and_check_revoked_tenant(tenant_client, id_token):
  try:
    # Verify the ID token while checking if the token is revoked by
    # passing check_revoked=True.
    decoded_token = tenant_client.verify_id_token(id_token, check_revoked=True)
    # Token is valid and not revoked.
    uid = decoded_token['uid']
    print(uid)
  except tenant_mgt.TenantIdMismatchError:
    # Token belongs to a different tenant.
    pass
  except auth.RevokedIdTokenError:
    # Token revoked, inform the user to reauthenticate or signOut().
    pass
  except auth.UserDisabledError:
    # Token belongs to a disabled user record.
    pass
  except auth.InvalidIdTokenError:
    # Token is invalid
    pass


### Controlling access with custom claims ###
## Set admin privilege on the user corresponding to uid.
def custom_claims_set_tenant(tenant_client, uid):
  tenant_client.set_custom_user_claims(uid, {'admin': True})


## After verifying the ID token and decoding its payload, the additional custom claims can then be checked to enforce access control.
def custom_claims_verify_tenant(tenant_client, id_token):
  # [START verify_custom_claims_tenant]
  # Verify the ID token first.
  claims = tenant_client.verify_id_token(id_token)
  if claims['admin'] is True:
    # Allow access to requested admin resource.
    print('True')
    pass


# [END verify_custom_claims_tenant]

## Custom claims for an existing user for a specific tenant are also available as a property on the user record.
def custom_claims_read_tenant(tenant_client, uid):
  user = tenant_client.get_user(uid)

  # The claims can be accessed on the user record.
  print(user.custom_claims.get('admin'))


### Generating email action links
def generate_email_verification_link_tenant(tenant_client):
  action_code_settings = auth.ActionCodeSettings(
      url='https://www.example.com/checkout?cartId=1234',
      handle_code_in_app=True,
      ios_bundle_id='com.example.ios',
      android_package_name='com.example.android',
      android_install_app=True,
      android_minimum_version='12',
      # FDL custom domain.
      dynamic_link_domain='coolapp.page.link',
  )

  email = 'test2@gmail.com'
  link = tenant_client.generate_email_verification_link(
      email, action_code_settings
  )
  # Construct email from a template embedding the link, and send
  # using a custom SMTP server.
  send_custom_email(email, link)


# not in doc
def send_custom_email(email, link):
  del email
  del link


##### END of DOC

# Put tenant_id, uid, and id_token
tenant_id = ''
tenant_client = get_tenant_client(tenant_id)
uid = ''
id_token = ''
# Call the functions you want to test here
print('----')
print('----')