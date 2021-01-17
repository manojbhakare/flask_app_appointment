from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with, marshal
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import datetime as dt
import copy

# initialize Flask object
app = Flask(__name__)
api = Api(app)
# configure sqlite uri
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database1.db'
db = SQLAlchemy(app)


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'manoj.bhakare007@gmail.com'
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


slots = {"1": "9:30", "2": "10:00", "3": "10:30", "4": "11:00", "5": "11:30", "6":
         "12:00", "7": "12:30",
         "8": "13:00", "9": "13:30", "10": "14:00", "11":
             "14:30", "12": "15:00", "13": "15:30", "14": "16:00"}

# appointment model for appointments


class AppointmentModel(db.Model):
    apt_id = db.Column(db.Integer, primary_key=True)
    slot = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(10), nullable=False)
    endtime = db.Column(db.DateTime, nullable=False)
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    doctor_id = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)


book_appointment_args = reqparse.RequestParser()
book_appointment_args.add_argument(
    "slot", type=str, help="Slot is required")
book_appointment_args.add_argument(
    "date", type=str, help="Date is required")
book_appointment_args.add_argument(
    "user_id", type=int, help="user_id is required")
book_appointment_args.add_argument(
    "doctor_id", type=int, help="doctor_id is required")

# resource fiels to marshal_with class object
resource_fields = {
    'apt_id': fields.Integer,
    'slot': fields.String,
    'status': fields.String,
    'date': fields.String,
    'endtime': fields.DateTime,
    'user_id': fields.Integer,
    'doctor_id': fields.Integer,
    'timestamp': fields.DateTime,
}

# send mail url for sending sheduled mail of active appointments to admin daily


@app.route("/test")
def test():
    print(dt.datetime.now())
    return "success"


@app.route("/sendmail")
def sendmail():
    recipients = ["manoj.bhakare007@gmail.com"]
    sender = 'manoj.bhakare007@gmail.com'
    d = dt.date.today()
    date = d.strftime('%Y-%m-%d')
    msg = Message('Active appoints on '+date,
                  sender=sender, recipients=recipients)
    res = getActiveAppoinmentstoday()

    msg.html = res
    mail.send(msg)

    return "send"


# cron job url to inactive appointments which are expired


@app.route('/turninactive')
def turnInactiveAppointments():
    today = dt.datetime.now()
    result = AppointmentModel.query.filter(
        AppointmentModel.endtime <= today, AppointmentModel.status != 'expired', AppointmentModel.status != 'attended').all()
    for a in result:
        a.status = "expired"
    db.session.commit()
    count = len(result)
    print("executed", today)
    return str(count)

# active appointments to send email to admin


@app.route('/active')
def getActiveAppoinmentstoday():
    d = dt.date.today()
    date1 = dt.datetime.strptime(d.strftime('%Y%m%d'), '%Y%m%d')
    result = AppointmentModel.query.filter_by(
        date=d, status="approved").all()
    res = "<table> <tr> <th>Doctor</th><th>user</th><th>Time</th></tr>"
    if result:
        for apt in result:
            row = "<tr><td>"+str(apt.doctor_id)+"</td><td>" + \
                str(apt.user_id)+"</td><td>"+slots[apt.slot]+"</td></tr>"
            res = res+row
    res = res+"</table>"
    return res


@app.route('/')
def index():
    return("Welcome to Appointment Management")


get_allslots_args = reqparse.RequestParser()
get_allslots_args.add_argument(
    "date", type=str, help="Date is Required")
get_allslots_args.add_argument("user_id", type=str, help="user_id is required")
get_allslots_args.add_argument(
    "doctor_id", type=str, help="Doctor_id is required")

# get all avialabe slots for particular day for


class GetAllSlots(Resource):
    def get(self):
        args = get_allslots_args.parse_args()
        date = dt.datetime.strptime(args['date'], '%Y-%m-%d').date()
        today = dt.datetime.now()
        bookingdayendtime = dt.datetime.strptime(
            str(date.year)+"-"+str(date.month)+"-"+str(date.day)+" 16:00", '%Y-%m-%d %H:%M')
        print(bookingdayendtime, today, date)
        if today > bookingdayendtime:
            abort(409, message="Slot time must be greater than todays time")
        result1 = AppointmentModel.query.filter_by(
            date=date, doctor_id=args['doctor_id'], user_id=args['user_id']).all()
        if result1:
            abort(409, message="user has already booked an appointment")
        result = AppointmentModel.query.filter_by(
            date=date, doctor_id=args['doctor_id']).all()
        temp = copy.deepcopy(slots)
        for slot in result:
            temp.pop(slot.slot)
        for k, v in slots.items():
            startdate = dt.datetime.strptime(
                args['date']+" "+v, '%Y-%m-%d %H:%M')
            if today > startdate:
                if k in temp.keys():
                    temp.pop(k)
        return {"data": temp, "message": "success"}, 200


api.add_resource(GetAllSlots, "/api/slots")


class ApplyAppoinment(Resource):
    def post(self):
        args = book_appointment_args.parse_args()
        date = dt.datetime.strptime(args['date'], '%Y-%m-%d').date()
        startdate = dt.datetime.strptime(
            args['date']+" "+slots[args['slot']], '%Y-%m-%d %H:%M')
        endtime = startdate + dt.timedelta(minutes=30)
        if startdate < dt.datetime.now():
            abort(409, message="appoinment date must be greater then current time")
        result = AppointmentModel.query.filter_by(
            date=date, doctor_id=args['doctor_id'], slot=args['slot']).all()
        if result:
            abort(409, message="This slot is alredy taken")
        result1 = AppointmentModel.query.filter_by(
            date=date, doctor_id=args['doctor_id'], user_id=args['user_id']).all()
        if result1:
            abort(409, message="User can apply for only one appointment for the day")
        apt = AppointmentModel(slot=args['slot'], status="apply", date=date,
                               user_id=args['user_id'], endtime=endtime, doctor_id=args['doctor_id'],
                               timestamp=dt.datetime.now())
        db.session.add(apt)
        db.session.commit()
        return {"data": marshal(apt, resource_fields), "message": "Appointment Applied Success"}, 201


api.add_resource(ApplyAppoinment, "/api/applyappointment")


class ApproveAppointment(Resource):
    # S@marshal_with(resource_fields)
    def patch(self, apt_id):
        result = AppointmentModel.query.filter_by(apt_id=apt_id).first()
        if not result:
            abort(404, message="Could not find appointment id : "+str(apt_id))
        if 'approved' == result.status:
            abort(409, message="Appoinment is alredy  approved")
        if result.status not in ('apply'):
            abort(409, message="Only apply Appointments can be approved ")
        result.status = 'approved'
        db.session.commit()
        return {"data": marshal(result, resource_fields), "message": "Approved Sucessfully"}, 202


api.add_resource(ApproveAppointment,
                 "/api/app/approved/<int:apt_id>")


class AttendAppointment(Resource):
    # S@marshal_with(resource_fields)
    def patch(self, apt_id):
        result = AppointmentModel.query.filter_by(apt_id=apt_id).first()
        if not result:
            abort(404, message="Could not find appointment id : "+str(apt_id))
        if 'attended' == result.status:
            abort(409, message="Appoinment is alredy  attended")
        if result.status not in ('approved'):
            abort(409, message="Only approved Appointments can be Attended ")
        result.status = 'attended'
        db.session.commit()
        return {"data": marshal(result, resource_fields), "message": "Attended Sucessfully"}, 202


api.add_resource(AttendAppointment,
                 "/api/app/attended/<int:apt_id>")


class GetActiveAppointments(Resource):
    def get(self, date, status):
        date1 = dt.datetime.strptime(date, '%Y-%m-%d').date()
        result = AppointmentModel.query.filter_by(
            date=date1, status=status).all()
        if not result:
            abort(404, message="Could not find appointments on : "+date)
        response = {"data": marshal(
            result, resource_fields), "message": "sucess"}
        return response


api.add_resource(GetActiveAppointments,
                 "/api/get-appointments/<string:date>/<string:status>")


if __name__ == "__main__":

    app.run(host="0.0.0.0", debug=True)
