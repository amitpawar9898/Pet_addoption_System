import os
import sys
import subprocess
import time
from flask import Flask, render_template, request

# Ensure required packages are installed. If not, try to install them automatically
def _ensure_packages():
	try:
		import flask_sqlalchemy  # noqa: F401
		import sqlalchemy  # noqa: F401
		import dotenv  # noqa: F401
	except Exception:
		print("Required DB packages not found. Installing: Flask-SQLAlchemy, SQLAlchemy, pymysql, python-dotenv")
		try:
			subprocess.check_call([sys.executable, "-m", "pip", "install", "Flask-SQLAlchemy", "SQLAlchemy", "pymysql", "python-dotenv"])
		except subprocess.CalledProcessError as e:
			print("Automatic install failed:", e)
			print("Please activate your virtualenv and run: pip install Flask-SQLAlchemy SQLAlchemy pymysql python-dotenv")
			raise


_ensure_packages()

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from dotenv import load_dotenv

load_dotenv()

# Initialize SQLAlchemy
db = SQLAlchemy()

# Define Pet model (SQLAlchemy)
class Pet(db.Model):
	__tablename__ = 'pets'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(120), nullable=False)
	species = db.Column(db.String(50))
	breed = db.Column(db.String(120))
	age_years = db.Column(db.Float)
	sex = db.Column(db.String(10))
	size = db.Column(db.String(20))
	description = db.Column(db.Text)
	photo_url = db.Column(db.String(1024))
	status = db.Column(db.String(20), default='available')
	traits = db.Column(db.JSON)

# Sample pets data for initial load
PETS = [
	{
		"id": 1,
		"name": "Buddy",
		"species": "Dog",
		"breed": "Labrador Retriever",
		"age_years": 3.0,
		"sex": "male",
		"size": "large",
		"description": "Friendly and energetic, loves fetch and playing with other dogs. Great with children!",
		"photo_url": "https://images.unsplash.com/photo-1552053831-71594a27632d?q=80&w=1200&auto=format&fit=crop",
		"status": "available",
		"traits": ["Friendly", "Energetic", "Good with kids"]
	},
	{
		"id": 2,
		"name": "Mittens",
		"species": "Cat",
		"breed": "Tabby",
		"age_years": 2.5,
		"sex": "female",
		"size": "small",
		"description": "Calm lap cat who enjoys sunny windows and gentle pets. Perfect for a quiet home.",
		"photo_url": "https://images.unsplash.com/photo-1596854307943-279e29c90c14?q=80&w=1200&auto=format&fit=crop",
		"status": "available",
		"traits": ["Calm", "Independent", "Quiet"]
	},
	{
		"id": 3,
		"name": "Coco",
		"species": "Dog",
		"breed": "Mixed",
		"age_years": 1.0,
		"sex": "female",
		"size": "medium",
		"description": "Puppy who loves cuddles and walks. Very smart and eager to learn!",
		"photo_url": "https://images.unsplash.com/photo-1543466835-00a7907e9de1?q=80&w=1200&auto=format&fit=crop",
		"status": "available",
		"traits": ["Playful", "Smart", "Affectionate"]
	},
	{
		"id": 4,
		"name": "Tweety",
		"species": "Bird",
		"breed": "Budgie",
		"age_years": 1.5,
		"sex": "male",
		"size": "small",
		"description": "Colorful and cheerful budgie who loves to sing and interact. Already knows some words!",
		"photo_url": "https://images.unsplash.com/photo-1552728089-57bdde30beb3?q=80&w=1200&auto=format&fit=crop",
		"status": "available",
		"traits": ["Vocal", "Social", "Smart"]
	},
	{
		"id": 5,
		"name": "Hopper",
		"species": "Rabbit",
		"breed": "Dutch",
		"age_years": 2.0,
		"sex": "male",
		"size": "small",
		"description": "Gentle rabbit who loves to hop around and eat fresh vegetables. Litter box trained!",
		"photo_url": "https://images.unsplash.com/photo-1585110396000-c9ffd4e4b308?q=80&w=1200&auto=format&fit=crop",
		"status": "available",
		"traits": ["Gentle", "Clean", "Friendly"]
	},
	{
		"id": 6,
		"name": "Luna",
		"species": "Cat",
		"breed": "Persian",
		"age_years": 4.0,
		"sex": "female",
		"size": "medium",
		"description": "Elegant and graceful Persian cat who loves being groomed and getting attention.",
		"photo_url": "https://images.unsplash.com/photo-1573865526739-10659fec78a5?q=80&w=1200&auto=format&fit=crop",
		"status": "available",
		"traits": ["Elegant", "Affectionate", "Calm"]
	},
	{
		"id": 7,
		"name": "Rocky",
		"species": "Dog",
		"breed": "German Shepherd",
		"age_years": 5.0,
		"sex": "male",
		"size": "large",
		"description": "Well-trained and protective German Shepherd. Great guard dog with a loving personality.",
		"photo_url": "https://images.unsplash.com/photo-1589941013453-ec89f33b5e95?q=80&w=1200&auto=format&fit=crop",
		"status": "available",
		"traits": ["Protective", "Intelligent", "Loyal"]
	},
	{
		"id": 8,
		"name": "Hammy",
		"species": "Hamster",
		"breed": "Syrian Hamster",
		"age_years": 1.0,
		"sex": "male",
		"size": "tiny",
		"description": "Adorable Syrian hamster who loves running on his wheel and eating treats.",
		"photo_url": "https://images.unsplash.com/photo-1425082661705-1834bfd09dca?q=80&w=1200&auto=format&fit=crop",
		"status": "available",
		"traits": ["Active", "Curious", "Gentle"]
	}
]


def create_app():
	app = Flask(__name__, static_folder="static", template_folder="templates")
	app.config["SECRET_KEY"] = os.getenv("SESSION_SECRET", "dev_secret_change_me")

	# Try to use DATABASE_URL from environment; fallback to local SQLite if MySQL not available
	env_db = os.getenv('DATABASE_URL', 'mysql+pymysql://root:@127.0.0.1/pawfect')

	# Attempt to auto-start MySQL services / XAMPP if available, then retry connection
	def _try_start_mysql_services():
		"""Try to start common MySQL services on Windows or open XAMPP control panel.
		Returns True if a start command was issued, False otherwise."""
		started_any = False
		# Try common Windows service names
		service_names = ["MySQL80", "MySQL", "mysql"]
		for svc in service_names:
			try:
				# 'sc' is available on Windows; attempt to start - may require admin
				subprocess.run(["sc", "start", svc], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
				started_any = True
			except Exception:
				continue

		# If XAMPP present, open control panel to let user start MySQL
		xampp_path = r"C:\xampp\xampp-control.exe"
		if not started_any and os.path.exists(xampp_path):
			try:
				subprocess.Popen([xampp_path])
				started_any = True
			except Exception:
				pass

		return started_any

	# Attempt to verify connectivity to the configured DB with retries
	use_sqlite = False
	max_retries = 4
	retry_delay = 3  # seconds

	# If running on Windows, try to start services
	attempted_service_start = False
	if sys.platform.startswith('win'):
		attempted_service_start = _try_start_mysql_services()

	last_exc = None
	for attempt in range(1, max_retries + 1):
		try:
			test_engine = create_engine(env_db)
			with test_engine.connect() as conn:
				pass
			app.config['SQLALCHEMY_DATABASE_URI'] = env_db
			print(f"Using database from DATABASE_URL: {env_db}")
			last_exc = None
			break
		except Exception as e:
			last_exc = e
			print(f"DB connect attempt {attempt}/{max_retries} failed: {e}")
			time.sleep(retry_delay)

	if last_exc is not None:
		# couldn't connect to provided DB after retries, fall back to sqlite
		print(f"Warning: cannot connect to DATABASE_URL after retries ({last_exc}). Falling back to local SQLite.")
		sqlite_path = os.path.join(os.path.dirname(__file__), 'data')
		try:
			os.makedirs(sqlite_path, exist_ok=True)
		except Exception:
			pass
		sqlite_file = os.path.join(sqlite_path, 'dev.db')
		app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{sqlite_file}"
		use_sqlite = True

	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

	# Initialize the app with SQLAlchemy
	db.init_app(app)

	# Create tables (run once) inside app context
	with app.app_context():
		try:
			db.create_all()
			if use_sqlite:
				print(f"SQLite DB created at {sqlite_file}")
			else:
				print("Tables created/verified on configured DB.")
		except Exception as create_err:
			print(f"Error creating tables: {create_err}")

	@app.route("/")
	def home():
		return render_template("index.html", title="Pawfect Home - Adopt a Friend")


	@app.route("/pets")
	def pets_list():
		available = [p for p in PETS if p.get("status") == "available"]
		return render_template("pets/list.html", title="Available Pets", pets=available)

	@app.route("/pets/<int:pet_id>")
	def pet_detail(pet_id: int):
		pet = next((p for p in PETS if p["id"] == pet_id), None)
		if not pet:
			return render_template("404.html", title="Not Found"), 404
		return render_template("pets/detail.html", title=pet["name"], pet=pet)

	@app.route("/adoptions/apply", methods=["POST"])
	def adoption_apply():
		# Demo: just accept the form and show a thank-you page (no DB)
		_ = {
			"pet_id": request.form.get("pet_id"),
			"applicant_name": request.form.get("applicant_name"),
			"applicant_email": request.form.get("applicant_email"),
			"message": request.form.get("message"),
		}
		return render_template("adoptions/thankyou.html", title="Application Submitted")

	@app.errorhandler(404)
	def not_found(_):
		return render_template("404.html", title="Not Found"), 404

	@app.route("/how-it-works")
	def how_it_works():
		return render_template("how_it_works.html", title="How it works")

	@app.route("/about")
	def about():
		return render_template("about.html", title="About")

	@app.route("/care-guide")
	def care_guide():
		return render_template("care_guide.html", title="Pet Care Guide")

	@app.route("/vaccination", methods=["GET", "POST"])
	def vaccination():
		if request.method == "POST":
			# In a real app, this would save to a database
			appointment = {
				"pet_type": request.form.get("pet_type"),
				"vaccination_type": request.form.get("vaccination_type"),
				"preferred_date": request.form.get("preferred_date"),
				"owner_name": request.form.get("owner_name"),
				"phone": request.form.get("phone"),
				"email": request.form.get("email")
			}
			return render_template("vaccination_booked.html", 
								 title="Appointment Confirmed",
								 appointment=appointment)
		return render_template("vaccination.html", title="Pet Vaccination Services")

	@app.route("/donate", methods=["GET", "POST"])
	def donate():
		if request.method == "POST":
			# Process donation (this is a demo - you would integrate with a payment gateway in production)
			amount = request.form.get("amount", 0)
			donation_type = request.form.get("donation_type", "one-time")
			return render_template("donate_success.html", 
								 title="Thank You!", 
								 amount=amount,
								 donation_type=donation_type)
		return render_template("donate.html", title="Support Our Cause")
	@app.route("/contact", methods=["GET", "POST"])
	def contact():
		if request.method == "POST":
			# Demo: no persistence; show a simple thank-you page
			return render_template("adoptions/thankyou.html", title="Message sent")
		return render_template("contact.html", title="Contact")

	@app.route("/signup", methods=["GET", "POST"])
	def signup():
		if request.method == "POST":
			# In a real app, you'd create a user record. Here we just show a thank-you page.
			return render_template("adoptions/thankyou.html", title="Account Created")
		return render_template("signup.html", title="Create Account")

	@app.route("/signin", methods=["GET", "POST"])
	def signin():
		if request.method == "POST":
			# Demo: no auth; in production verify credentials and create a session
			return render_template("adoptions/thankyou.html", title="Signed In")
		return render_template("signin.html", title="Sign In")

	@app.route("/billing")
	def billing():
		return render_template("billing.html", title="Payment Options")

	@app.route("/process-payment", methods=["POST"])
	def process_payment():
		# Demo: In production, integrate with a payment gateway like Stripe
		payment_type = request.form.get("payment_type")
		amount = request.form.get("amount")
		
		# Process different payment types
		if payment_type == "adoption":
			pet_name = request.form.get("pet_name")
			# Process adoption payment
			return render_template("payment_success.html", 
								 title="Payment Successful",
								 amount=amount,
								 pet_name=pet_name)
		
		elif payment_type == "vaccination":
			vac_type = request.form.get("vac_type")
			vac_date = request.form.get("vac_date")
			# Process vaccination payment
			return render_template("payment_success.html",
								 title="Vaccination Scheduled",
								 vac_type=vac_type,
								 vac_date=vac_date)
		
		elif payment_type == "sponsorship":
			# Process monthly sponsorship
			return render_template("payment_success.html",
								 title="Sponsorship Started",
								 amount=amount,
								 recurring=True)
		
		return "Invalid payment type", 400

	return app

if __name__ == "__main__":
	port = int(os.getenv("PORT", "3000"))
	app = create_app()
	app.run(host="0.0.0.0", port=port, debug=True)


