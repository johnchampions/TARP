import facebook

token = 'EAAZAAISS4zo0BAPOtQU4uZBULiBjG2BrMCQGh7dO3IkhywFanXiFbrACHYXLyl3R6GrbRgJAjeUhva4Mn2Kz8riZChJQZAjsM7OzqRZAckQPwb9UmSKcRRAUETSfkBzVB6sEeS5ajA9ZCIXXigDm1ZBZCRbRJMmE9lj3ii6nbsaY88Dlj0FTu0F5mYDX5AtGWvv6SGShEU0u1fKWxvZBupO2mSZBUK9KSi0QoZD'
graph = facebook.GraphAPI(access_token=token, version=3.1)
events = graph.request('/search?q=Poetry&type=event&limit=10000')
eventslist = events['data']
eventid = eventslist[1]['id']

event1 = graph.get_object(id=eventid)
print(event1)
