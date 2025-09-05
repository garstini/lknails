from django.core.management.base import BaseCommand
from salon.models import Appointment, AppointmentService, Service, Customer


class Command(BaseCommand):
    help = 'Debug appointment and service mapping issues'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Debug Appointment và Service Mapping ===\n'))
        
        # Check appointments
        appointments = Appointment.objects.all().order_by('-created_at')[:10]
        
        if not appointments:
            self.stdout.write(self.style.WARNING('❌ Không có appointment nào trong database'))
            return
        
        for appointment in appointments:
            self.stdout.write(f'\n📅 Appointment #{appointment.id}')
            self.stdout.write(f'   Khách hàng: {appointment.customer.user.get_full_name()}')
            self.stdout.write(f'   Ngày: {appointment.date} {appointment.time}')
            self.stdout.write(f'   Trạng thái: {appointment.status}')
            self.stdout.write(f'   Tổng giá: €{appointment.total_price}')
            self.stdout.write(f'   Tổng thời gian: {appointment.total_duration} phút')
            
            # Check services through ManyToMany
            services_m2m = appointment.services.all()
            self.stdout.write(f'   Services (M2M): {services_m2m.count()} services')
            for service in services_m2m:
                self.stdout.write(f'     - {service.name} (€{service.price}, {service.duration_minutes}min)')
            
            # Check services through AppointmentService
            try:
                appointment_services = appointment.appointmentservice_set.all()
            except AttributeError:
                from salon.models import AppointmentService
                appointment_services = AppointmentService.objects.filter(appointment=appointment)
            
            self.stdout.write(f'   AppointmentService records: {appointment_services.count()} records')
            for app_service in appointment_services:
                self.stdout.write(f'     - {app_service.service.name} (€{app_service.price_at_booking}, {app_service.duration_at_booking}min)')
            
            if services_m2m.count() != appointment_services.count():
                self.stdout.write(self.style.ERROR('   ❌ MỜI THẤY VẤN ĐỀ: Số lượng services khác nhau giữa M2M và AppointmentService!'))
        
        # Check recent services
        self.stdout.write(f'\n📋 Active Services: {Service.objects.filter(is_active=True).count()}')
        for service in Service.objects.filter(is_active=True)[:5]:
            self.stdout.write(f'   - {service.name} (€{service.price}, {service.duration_minutes}min)')
            
        self.stdout.write('\n🎯 Debug hoàn tấthành!')