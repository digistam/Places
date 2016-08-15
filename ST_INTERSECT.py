import httplib2
import apiclient
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from apiclient import errors

try:
        credentials = ServiceAccountCredentials.from_json_keyfile_name('IOT-***.json', scopes="https://www.googleapis.com/auth/fusiontables")
        http = httplib2.Http()
        http = credentials.authorize(http)
        service = build("fusiontables","v2",http=http)
        try:
                query = service.query().sql(
                        sql=('SELECT Callsign, Snapshot, Airline '
                                'FROM 1****P '
                                'WHERE ST_INTERSECTS('
                                'Trail, '
                                # define bounding box
                                'RECTANGLE('
                                # lower left corner
                                'LATLNG(52.917739, 4.772443),'
                                # upper right corner
                                'LATLNG(52.929304, 4.792227)))')
                        ).execute()
                print query['rows']
        except apiclient.errors.HttpError,e:
                print 'error'
                print e
except apiclient.errors.HttpError, e:
        print 'error'
        print e
