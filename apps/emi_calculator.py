from flask import Blueprint, render_template, request

# Create a Blueprint for the EMI calculator
# The first argument is the blueprint name.
# The second argument is the import name, typically __name__.
# The third argument, template_folder, tells the blueprint where to find its templates.
emi_bp = Blueprint('emi_calculator', __name__, template_folder='templates', url_prefix='/emi-calculator')

def calculate_emi(principal, annual_rate, years):
    """Calculates Equated Monthly Installment (EMI)."""
    if principal <= 0 or annual_rate < 0 or years <= 0:
        return None

    monthly_rate = (annual_rate / 100) / 12
    months = years * 12

    if monthly_rate == 0: # Handle zero interest rate case
        return principal / months

    emi = principal * monthly_rate * ( (1 + monthly_rate) ** months ) / ( (1 + monthly_rate) ** months - 1)
    return emi

@emi_bp.route('/', methods=['GET', 'POST'])
def emi_page():
    emi_result = None
    error_message = None
    form_data = {}

    if request.method == 'POST':
        try:
            principal = float(request.form.get('principal'))
            annual_rate = float(request.form.get('annual_rate'))
            years = int(request.form.get('years'))

            form_data = {'principal': principal, 'annual_rate': annual_rate, 'years': years}

            if principal <= 0:
                error_message = "Principal amount must be greater than zero."
            elif annual_rate < 0:
                 error_message = "Annual interest rate cannot be negative."
            elif years <= 0:
                error_message = "Loan term (years) must be greater than zero."
            else:
                emi_result = calculate_emi(principal, annual_rate, years)
                if emi_result is None: # Should be caught by above checks, but as a fallback
                    error_message = "Could not calculate EMI with the provided values."

        except ValueError:
            error_message = "Invalid input. Please enter valid numbers."
        except Exception as e:
            error_message = f"An unexpected error occurred: {e}"

    return render_template('emi_calculator/emi_form.html',
                           emi_result=emi_result,
                           error_message=error_message,
                           form_data=form_data)
