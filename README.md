# Appointment Management Service

## API Usage

All responses will have the form

```json
{
  "data": "Mixed type holding the content of the response",
  "message": "Description of what happened"
}
```

Subsequent response definitions will only detail the expected value of the `data field and message`
if any error occurs response contains message of what error has happened

### List all slots avilabale on a particular day

**Definition**

`GET /api/slots`

**Response**

- `200 OK` on success
- `409 CONFLICT` if requested date less then current time or user had alredy booked an appoinment with the doctor for the same day

```json
{
  "data": {
    "1": "9:30",
    "2": "10:00",
    "3": "10:30",
    "4": "11:00",
    "7": "12:30",
    "8": "13:00",
    "9": "13:30",
    "10": "14:00",
    "11": "14:30",
    "12": "15:00",
    "13": "15:30",
    "14": "16:00"
  },
  "message": "success"
}
```

**Arguments**

- `"date":Date` Date on which user wnats to book appointment date format must be `YYYY-mm-dd`
- `"doctor_id":int` Id of Doctor with whom appointment is to be apply
- `"user_id":int` the user who wnats to book the appointment

### Apply for an appointment

**Definition**

`POST /api/applyappointment`

**Arguments**

- `"date":Date` Date on which user wnats to book appointment date format must be `YYYY-mm-dd`
- `"doctor_id":int` Id of Doctor with whom appointment is to be apply
- `"user_id":int` the user who wnats to book the appointment
- `"slot":string` the slot user wants to apply for appointment slot value is between(1-14) refer `slots dictionary below`

All arguments are required default staus will be `apply`

**Response**

- `201 Created` on success
- `409 CONFLICT` if user try to apply same oppointment slot for same doctor on same day

```json
{
  "data": {
    "apt_id": 8,
    "slot": "4",
    "status": "apply",
    "date": "2021-01-19",
    "endtime": "Tue, 19 Jan 2021 11:30:00 -0000",
    "user_id": 2,
    "doctor_id": 3,
    "timestamp": "Sun, 17 Jan 2021 10:46:26 -0000"
  },
  "message": "Appointment Applied Success"
}
```

## Approve appointments by Aministrator

`PATCH /api/app/approved/<int:apt_id>`

**Parameters**

- `"user_id":int` the user_id whic need to be approved

**Response**

- `404 Not Found` if apt_id not found
- `202 Accepted` on success
- `409 CONFLICT` if apt_id is alredy aproved or only apply aplictions can be approved

```json
{
  "data": {
    "apt_id": 7,
    "slot": "4",
    "status": "approved",
    "date": "2021-01-17",
    "endtime": "Sun, 17 Jan 2021 11:30:00 -0000",
    "user_id": 2,
    "doctor_id": 3,
    "timestamp": "Sat, 16 Jan 2021 20:17:04 -0000"
  },
  "message": "Approved Sucessfully"
}
```

## Attended appointments by Aministrator

`PATCH /api/app/attented/<int:apt_id>`

**Parameters**

- `"user_id":int` the user_id which need to be attended

**Response**

- `404 Not Found` if apt_id not found
- `202 Accepted` on success
- `409 CONFLICT` if apt_id is alredy attended or only approved aplictions can be attended

```json
{
  "data": {
    "apt_id": 7,
    "slot": "4",
    "status": "attended",
    "date": "2021-01-17",
    "endtime": "Sun, 17 Jan 2021 11:30:00 -0000",
    "user_id": 2,
    "doctor_id": 3,
    "timestamp": "Sat, 16 Jan 2021 20:17:04 -0000"
  },
  "message": "Attended Sucessfully"
}
```

## Get appointment on particular day with status

`GET /api/get-appointments/<string:date>/<string:status>`

**Parameters**

- `"status":string` status of appointment it can be `attented,apply,expired or approved`
- `"date":string` Date on on which we want search `YYYY-mm-dd`

**Response**

- `404 Not Found` if appointments not found
- `200 OK` on success
  **Example**
  `http://localhost:5000/api/get-appointments/2021-01-17/attended`

```json
{
  "data": [
    {
      "apt_id": 6,
      "slot": "5",
      "status": "attended",
      "date": "2021-01-17",
      "endtime": "Sun, 17 Jan 2021 12:00:00 -0000",
      "user_id": 5,
      "doctor_id": 3,
      "timestamp": "Sat, 16 Jan 2021 16:40:13 -0000"
    },
    {
      "apt_id": 7,
      "slot": "4",
      "status": "attended",
      "date": "2021-01-17",
      "endtime": "Sun, 17 Jan 2021 11:30:00 -0000",
      "user_id": 2,
      "doctor_id": 3,
      "timestamp": "Sat, 16 Jan 2021 20:17:04 -0000"
    }
  ],
  "message": "sucess"
}
```

## send email to admin about details of daily appointment this

`GET /sendmail/<string:recipients>`

please configure emailid and password in source code before sending email
the email module doenot works in docker container amazon aws so to run it on localhost

**Parameters**

- `"recipients": string` Email id of admin to send mail

**Response**

- `200 OK` on success

`send`

## Deploy app on Docker

-`run command` docker-compose up

Docker file contains to configure Docker image build from `python:3` image

`cron-job file` contains two cron jobs
`1,31 9-18 * * * python3 /usr/src/app/cron-python.py >> /usr/src/app/cron-p.out`
first cron job is for deactivating the appointments which are not attented from schedule time setting status to expired it runs each half hour from 9 to 6 pm daily

- `8 * * * python3 /usr/src/app/cron-email.py >> /usr/src/app/cron-email.out`
  Second cron job is for sending email to admin regarding details of active appointments of the day at 8AM

### Database

sqlite database is used `database1.db` file for convinience
which stores appoints table
**fields_of_table**

```json
{
  "apt_id": fields.Integer,
  "slot": fields.String,
  "status": fields.String,
  "date": fields.String,
  "endtime": fields.DateTime,
  "user_id": fields.Integer,
  "doctor_id": fields.Integer,
  "timestamp": fields.DateTime
}
```

## Slots dictionary

```json
(slots = {
  "1": "9:30",
  "2": "10:00",
  "3": "10:30",
  "4": "11:00",
  "5": "11:30",
  "6": "12:00",
  "7": "12:30",
  "8": "13:00",
  "9": "13:30",
  "10": "14:00",
  "11": "14:30",
  "12": "15:00",
  "13": "15:30",
  "14": "16:00"
})
```

slots dictionary is used to map slot no with start time of slot
`End time is 30 after start time`
` keys of dict are slot no`
` values of dictionary are starttime of every slot`
