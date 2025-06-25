from flask import Blueprint, render_template, request

bmi_bp = Blueprint('bmi_calculator', __name__, template_folder='templates', url_prefix='/bmi-calculator')

def calculate_bmi(weight_kg, height_m):
    """Calculates Body Mass Index (BMI)."""
    if weight_kg <= 0 or height_m <= 0:
        return None
    bmi = weight_kg / (height_m ** 2)
    return bmi

def get_bmi_category(bmi):
    if bmi is None:
        return ""
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 24.9:
        return "Normal weight"
    elif 25 <= bmi < 29.9:
        return "Overweight"
    else: # bmi >= 30
        return "Obesity"

@bmi_bp.route('/', methods=['GET', 'POST'])
def bmi_page():
    bmi_result = None
    bmi_category = None
    error_message = None
    form_data = {}

    if request.method == 'POST':
        try:
            weight_kg = float(request.form.get('weight_kg'))
            height_cm = float(request.form.get('height_cm')) # Taking height in cm for user convenience

            form_data = {'weight_kg': weight_kg, 'height_cm': height_cm}

            if weight_kg <= 0:
                error_message = "Weight must be greater than zero."
            elif height_cm <= 0:
                error_message = "Height must be greater than zero."
            else:
                height_m = height_cm / 100 # Convert cm to meters for calculation
                bmi_result = calculate_bmi(weight_kg, height_m)
                if bmi_result is not None:
                    bmi_category = get_bmi_category(bmi_result)
                else:
                    # This case should ideally be caught by prior checks
                    error_message = "Could not calculate BMI with the provided values. Ensure inputs are positive."

        except ValueError:
            error_message = "Invalid input. Please enter valid numbers for weight and height."
        except Exception as e:
            error_message = f"An unexpected error occurred: {e}"

    return render_template('bmi_calculator/bmi_form.html',
                           bmi_result=bmi_result,
                           bmi_category=bmi_category,
                           error_message=error_message,
                           form_data=form_data)
