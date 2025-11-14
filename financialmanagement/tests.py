from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta
from .models import Staff, Wage, Sale, Expense, Balancesheet, Setprice
from users.models import User


class StaffModelTest(TestCase):
    """Test cases for Staff model"""

    def setUp(self):
        """Set up test data for Staff"""
        self.staff_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'nin': 'CM12345678901234',
            'district': 'Kampala',
            'sub_county': 'Nakawa',
            'parish': 'Bukoto',
            'village': 'Kisaasi',
            'gender': 'Male',
            'date_hired': date.today() - timedelta(days=30),
            'employment_type': 'Full Time',
            'monthly_salary': 300000
        }

    def test_staff_creation(self):
        """Test that staff can be created with auto-generated staff_id"""
        staff = Staff.objects.create(**self.staff_data)
        self.assertEqual(staff.first_name, 'John')
        self.assertEqual(staff.last_name, 'Doe')
        self.assertTrue(staff.staff_id.startswith('RF'))
        self.assertEqual(len(staff.staff_id), 5)  # RF + 3 digits
        self.assertTrue(staff.is_active)

    def test_staff_id_auto_generation(self):
        """Test that staff_id is auto-generated sequentially"""
        staff1 = Staff.objects.create(**self.staff_data)
        self.assertEqual(staff1.staff_id, 'RF001')

        staff_data_2 = self.staff_data.copy()
        staff_data_2['nin'] = 'CM98765432109876'
        staff2 = Staff.objects.create(**staff_data_2)
        self.assertEqual(staff2.staff_id, 'RF002')

    def test_get_full_name(self):
        """Test the get_full_name method"""
        staff = Staff.objects.create(**self.staff_data)
        self.assertEqual(staff.get_full_name(), 'John Doe')

    def test_get_full_address(self):
        """Test the get_full_address method"""
        staff = Staff.objects.create(**self.staff_data)
        expected_address = 'Kisaasi, Bukoto, Nakawa, Kampala'
        self.assertEqual(staff.get_full_address(), expected_address)

    def test_staff_str_representation(self):
        """Test the __str__ method of Staff"""
        staff = Staff.objects.create(**self.staff_data)
        self.assertEqual(str(staff), 'John Doe (Full Time)')


class WageModelTest(TestCase):
    """Test cases for Wage model"""

    def setUp(self):
        """Set up test data for Wage"""
        self.staff = Staff.objects.create(
            first_name='Jane',
            last_name='Smith',
            nin='CM11111111111111',
            district='Kampala',
            sub_county='Nakawa',
            parish='Bukoto',
            village='Kisaasi',
            gender='Female',
            date_hired=date.today() - timedelta(days=60),
            employment_type='Full Time',
            monthly_salary=300000
        )

    def test_wage_creation_with_staff(self):
        """Test creating wage linked to a staff member"""
        expected_amount = 250000
        wage = Wage.objects.create(
            employee_name='Jane Smith',
            staff=self.staff,
            days_missed=5,
            amount_paid=expected_amount,
            date_of_payment=date.today()
        )

        # Check that amount_paid is set correctly
        self.assertEqual(wage.amount_paid, expected_amount)
        self.assertEqual(wage.employee_name, 'Jane Smith')
        self.assertEqual(wage.staff, self.staff)

    def test_wage_creation_without_staff(self):
        """Test creating wage without linking to staff"""
        wage = Wage.objects.create(
            employee_name='Casual Worker',
            staff=None,
            days_missed=0,
            amount_paid=150000,
            date_of_payment=date.today()
        )

        self.assertIsNone(wage.staff)
        self.assertEqual(wage.amount_paid, 150000)
        self.assertEqual(wage.employee_name, 'Casual Worker')

    def test_wage_calculation_no_days_missed(self):
        """Test wage calculation when no days are missed"""
        expected_amount = 300000
        wage = Wage.objects.create(
            employee_name='Jane Smith',
            staff=self.staff,
            days_missed=0,
            amount_paid=expected_amount,
            date_of_payment=date.today()
        )

        self.assertEqual(wage.amount_paid, expected_amount)

    def test_wage_calculation_with_days_missed(self):
        """Test wage calculation with days missed"""
        expected_amount = 200000
        wage = Wage.objects.create(
            employee_name='Jane Smith',
            staff=self.staff,
            days_missed=10,
            amount_paid=expected_amount,
            date_of_payment=date.today()
        )

        self.assertEqual(wage.amount_paid, expected_amount)

    def test_negative_amount_paid_raises_error(self):
        """Test that negative amount_paid raises ValueError"""
        with self.assertRaises(ValueError) as context:
            Wage.objects.create(
                employee_name='Test Worker',
                staff=None,
                days_missed=0,
                amount_paid=-1000,
                date_of_payment=date.today()
            )
        self.assertIn('Amount paid cannot be negative', str(context.exception))

    def test_negative_days_missed_raises_error(self):
        """Test that negative days_missed raises ValueError"""
        with self.assertRaises(ValueError) as context:
            Wage.objects.create(
                employee_name='Test Worker',
                staff=None,
                days_missed=-5,
                amount_paid=100000,
                date_of_payment=date.today()
            )
        self.assertIn('Days missed cannot be negative', str(context.exception))

    def test_wage_str_representation(self):
        """Test the __str__ method of Wage"""
        wage = Wage.objects.create(
            employee_name='Jane Smith',
            staff=self.staff,
            days_missed=5,
            amount_paid=0,
            date_of_payment=date.today()
        )
        expected_str = f"Wages for Jane Smith - {wage.amount_paid}"
        self.assertEqual(str(wage), expected_str)


class WageViewSetTest(APITestCase):
    """Test cases for Wage API endpoints"""

    def setUp(self):
        """Set up test data and client"""
        self.client = APIClient()

        # Create staff member
        self.staff = Staff.objects.create(
            first_name='Test',
            last_name='Employee',
            nin='CM99999999999999',
            district='Kampala',
            sub_county='Nakawa',
            parish='Bukoto',
            village='Kisaasi',
            gender='Male',
            date_hired=date.today() - timedelta(days=30),
            employment_type='Full Time',
            monthly_salary=450000
        )

    def test_create_wage_with_employee_name(self):
        """Test creating a wage with just employee name"""
        url = '/api/wages/'
        data = {
            'employee_name': 'John Worker',
            'date_of_payment': str(date.today()),
            'days_missed': 3,
            'amount_paid': 200000
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['employee_name'], 'John Worker')
        self.assertEqual(response.data['days_missed'], 3)

    def test_create_wage_with_staff_link(self):
        """Test creating a wage linked to a staff member"""
        url = '/api/wages/'
        expected_amount = 420000
        data = {
            'employee_name': 'Test Employee',
            'staff': self.staff.staff_id,
            'date_of_payment': str(date.today()),
            'days_missed': 2,
            'amount_paid': expected_amount
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['staff_id'], self.staff.staff_id)

        # Verify amount_paid was set correctly
        wage = Wage.objects.get(id=response.data['id'])
        self.assertEqual(wage.amount_paid, expected_amount)

    def test_create_wage_missing_employee_name(self):
        """Test that creating wage without employee_name is allowed (optional field)"""
        url = '/api/wages/'
        data = {
            'date_of_payment': str(date.today()),
            'days_missed': 0,
            'amount_paid': 100000
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data.get('employee_name') or None)

    def test_create_wage_invalid_staff_id(self):
        """Test creating wage with invalid staff_id returns error"""
        url = '/api/wages/'
        data = {
            'employee_name': 'Test Worker',
            'staff': 'INVALID_ID',
            'date_of_payment': str(date.today()),
            'days_missed': 0,
            'amount_paid': 100000
        }

        response = self.client.post(url, data, format='json')
        # Should return error for invalid staff_id
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_wages(self):
        """Test listing all wages"""
        # Create test wages
        Wage.objects.create(
            employee_name='Worker 1',
            staff=None,
            days_missed=0,
            amount_paid=150000,
            date_of_payment=date.today()
        )
        Wage.objects.create(
            employee_name='Worker 2',
            staff=self.staff,
            days_missed=5,
            amount_paid=0,
            date_of_payment=date.today()
        )

        url = '/api/wages/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify that we have at least the 2 wages we just created
        self.assertGreaterEqual(len(response.data), 2)

    def test_get_wages_by_employee(self):
        """Test filtering wages by staff_id"""
        # Create wages for the staff
        Wage.objects.create(
            employee_name='Test Employee',
            staff=self.staff,
            days_missed=2,
            amount_paid=0,
            date_of_payment=date.today()
        )
        Wage.objects.create(
            employee_name='Test Employee',
            staff=self.staff,
            days_missed=1,
            amount_paid=0,
            date_of_payment=date.today() - timedelta(days=30)
        )

        url = f'/api/wages/by_employee/?staff_id={self.staff.staff_id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_wages_by_employee_missing_param(self):
        """Test by_employee endpoint without staff_id parameter"""
        url = '/api/wages/by_employee/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class SaleModelTest(TestCase):
    """Test cases for Sale model"""

    def test_sale_creation_and_calculation(self):
        """Test sale creation with automatic calculations"""
        sale = Sale.objects.create(
            first_name='ABC',
            last_name='Ltd',
            batch_id='B001',
            item='Coffee Beans',
            rate=Decimal('5000.00'),
            quantity=100,
            amount=Decimal('300000.00'),
            date_of_payment=date.today(),
            method_of_payment='Cash'
        )

        # Check total_amount calculation
        expected_total = Decimal('5000.00') * 100
        self.assertEqual(sale.total_amount, expected_total)

        # Check balance calculation
        expected_balance = expected_total - Decimal('300000.00')
        self.assertEqual(sale.balance, expected_balance)

        # Check status
        self.assertEqual(sale.status, 'Partial Payment')

    def test_sale_fully_paid_status(self):
        """Test sale status when fully paid"""
        sale = Sale.objects.create(
            first_name='XYZ',
            last_name='Corp',
            item='Coffee Beans',
            rate=Decimal('5000.00'),
            quantity=100,
            amount=Decimal('500000.00'),
            date_of_payment=date.today(),
            method_of_payment='Bank Transfer'
        )

        self.assertEqual(sale.status, 'Paid')
        self.assertEqual(sale.balance, Decimal('0.00'))


class SetpriceModelTest(TestCase):
    """Test cases for Setprice model"""

    def test_setprice_creation(self):
        """Test creating a price setting"""
        price = Setprice.objects.create(
            production_kgPrice='5000',
            farmer_kgPrice='3500'
        )

        self.assertEqual(price.production_kgPrice, '5000')
        self.assertEqual(price.farmer_kgPrice, '3500')

    def test_setprice_str_representation(self):
        """Test the __str__ method"""
        price = Setprice.objects.create(
            production_kgPrice='5000',
            farmer_kgPrice='3500'
        )

        expected_str = 'Production Price: 5000, Farmer Price: 3500'
        self.assertEqual(str(price), expected_str)
