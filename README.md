# firebase-admin-python-snippets-test
Test app for Firebase Admin Python SDK code snippets

Steps for using test-app.py file to test code snippets in https://github.com/firebase/firebase-admin-python/blob/master/snippets/auth/index.py:

1.  Clone this repository

1.  Install the Admin SDK Python by running

    ```
    pip install --user firebase-admin
    ```
    Or https://firebase.google.com/docs/admin/setup#add-sdk

1.  Download your Firebase project's service account key

    `In Firebase Console > Project settings > Service accounts > Generate new
    private key`

1.  Set `PATH_TO_SERVICE_ACCOUNT_KEY` to the path to your generated service account key (line 9)

    Optional: Put your `tenant_id`, `uid`, and `id_token` (line 332-335)

1.  Add new or existing functions that you want to test

1.  Call functions at the end of the file and verify whether the functions work
    at Google Cloud console