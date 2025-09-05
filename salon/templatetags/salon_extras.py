from django import template

register = template.Library()

@register.filter
def service_demo_image(service):
    """Return a demo image URL for a service based on its name"""
    
    # Beautiful nail and lash demo images mapping
    service_images = {
        # New Nail Services from LK website
        'Maniküre Classic': 'https://images.unsplash.com/photo-1604654894610-df63bc536371?w=400&h=300&fit=crop&auto=format',
        'Pediküre Classic': 'https://images.unsplash.com/photo-1576013551627-0cc20b96c2a7?w=400&h=300&fit=crop&auto=format',
        'Gel Maniküre Neumodellage': 'https://images.unsplash.com/photo-1560457079-9a6532ccb118?w=400&h=300&fit=crop&auto=format',
        'Gel Maniküre Auffüllen': 'https://images.unsplash.com/photo-1616394584738-fc6e612e71b9?w=400&h=300&fit=crop&auto=format',
        'Gel Pediküre Neumodellage': 'https://images.unsplash.com/photo-1519014816548-bf5fe059798b?w=400&h=300&fit=crop&auto=format',
        'Gel Pediküre Auffüllen': 'https://images.unsplash.com/photo-1567721913486-6585f069b332?w=400&h=300&fit=crop&auto=format',
        'Nail Art Design Basic': 'https://images.unsplash.com/photo-1614252369475-531eba835eb1?w=400&h=300&fit=crop&auto=format',
        'Nail Art Design Premium': 'https://images.unsplash.com/photo-1643073875337-b1b8e2b1daf5?w=400&h=300&fit=crop&auto=format',
        'French Maniküre': 'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=400&h=300&fit=crop&auto=format',
        'Ombre Nails': 'https://images.unsplash.com/photo-1614252369475-531eba835eb1?w=400&h=300&fit=crop&auto=format',
        'Nagelverlängerung mit Schablone': 'https://images.unsplash.com/photo-1616394584738-fc6e612e71b9?w=400&h=300&fit=crop&auto=format',
        'Nagelverlängerung mit Tips': 'https://images.unsplash.com/photo-1604654894610-df63bc536371?w=400&h=300&fit=crop&auto=format',

        # New Lash Services  
        'Classic Lashes 1:1': 'https://images.unsplash.com/photo-1587614382346-4ec70e388b28?w=400&h=300&fit=crop&auto=format',
        'Light Volume 2D-3D': 'https://images.unsplash.com/photo-1585652757141-bf4a4aa786c0?w=400&h=300&fit=crop&auto=format',
        'Volume 4D-5D': 'https://images.unsplash.com/photo-1580870069867-74c57ee1bb07?w=400&h=300&fit=crop&auto=format',
        'Mega Volume ab 6D': 'https://images.unsplash.com/photo-1588681664899-f142ff2dc9b1?w=400&h=300&fit=crop&auto=format',
        'Wimpern Refill 2-3 Wochen': 'https://images.unsplash.com/photo-1587614382346-4ec70e388b28?w=400&h=300&fit=crop&auto=format',
        'Wimpern Refill 4+ Wochen': 'https://images.unsplash.com/photo-1585652757141-bf4a4aa786c0?w=400&h=300&fit=crop&auto=format',
        'Wimpernlifting': 'https://images.unsplash.com/photo-1581342748008-aac7a5a6712a?w=400&h=300&fit=crop&auto=format',
        'Wimpernlifting + Färbung': 'https://images.unsplash.com/photo-1581342748008-aac7a5a6712a?w=400&h=300&fit=crop&auto=format',
        'Wimpern Entfernung': 'https://images.unsplash.com/photo-1585652757141-bf4a4aa786c0?w=400&h=300&fit=crop&auto=format',

        # Special Services
        'Paraffin-Behandlung Hände': 'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=400&h=300&fit=crop&auto=format',
        'Paraffin-Behandlung Füße': 'https://images.unsplash.com/photo-1519014816548-bf5fe059798b?w=400&h=300&fit=crop&auto=format',
        'Augenbrauen Styling': 'https://images.unsplash.com/photo-1580618672591-eb180b1a973f?w=400&h=300&fit=crop&auto=format',
        'Augenbrauen Färbung': 'https://images.unsplash.com/photo-1542068829-1115f0b7c4ae?w=400&h=300&fit=crop&auto=format',
        'Beauty-Paket Complete': 'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=400&h=300&fit=crop&auto=format',

        # Keep some old services for backward compatibility
        'Classic Manicure': 'https://images.unsplash.com/photo-1604654894610-df63bc536371?w=400&h=300&fit=crop&auto=format',
        'French Manicure': 'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=400&h=300&fit=crop&auto=format',
        'Gel Manicure': 'https://images.unsplash.com/photo-1560457079-9a6532ccb118?w=400&h=300&fit=crop&auto=format',
        'Express Manicure': 'https://images.unsplash.com/photo-1610992015732-2449b76344bc?w=400&h=300&fit=crop&auto=format',
        'Luxury Spa Manicure': 'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=400&h=300&fit=crop&auto=format',
        'Classic Pedicure': 'https://images.unsplash.com/photo-1576013551627-0cc20b96c2a7?w=400&h=300&fit=crop&auto=format',
        'Spa Pedicure': 'https://images.unsplash.com/photo-1519014816548-bf5fe059798b?w=400&h=300&fit=crop&auto=format',
        'Gel Pedicure': 'https://images.unsplash.com/photo-1560457079-9a6532ccb118?w=400&h=300&fit=crop&auto=format',
        'Medical Pedicure': 'https://images.unsplash.com/photo-1487296744692-5514d8983738?w=400&h=300&fit=crop&auto=format',
        'Express Pedicure': 'https://images.unsplash.com/photo-1567721913486-6585f069b332?w=400&h=300&fit=crop&auto=format',
        'Nail Art (Simple)': 'https://images.unsplash.com/photo-1614252369475-531eba835eb1?w=400&h=300&fit=crop&auto=format',
        'Nail Art (Complex)': 'https://images.unsplash.com/photo-1643073875337-b1b8e2b1daf5?w=400&h=300&fit=crop&auto=format',
        'Acrylic Nails (Full Set)': 'https://images.unsplash.com/photo-1616394584738-fc6e612e71b9?w=400&h=300&fit=crop&auto=format',
        'Acrylic Nails (Refill)': 'https://images.unsplash.com/photo-1616394584738-fc6e612e71b9?w=400&h=300&fit=crop&auto=format',
        'Gel Extensions': 'https://images.unsplash.com/photo-1604654894610-df63bc536371?w=400&h=300&fit=crop&auto=format',
        'Nail Repair': 'https://images.unsplash.com/photo-1625699493798-c4abf1688d32?w=400&h=300&fit=crop&auto=format',
        'Nail Strengthening Treatment': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=300&fit=crop&auto=format',
        'Chrome Nails': 'https://images.unsplash.com/photo-1643073875337-b1b8e2b1daf5?w=400&h=300&fit=crop&auto=format',
        'Ombre/Gradient Nails': 'https://images.unsplash.com/photo-1614252369475-531eba835eb1?w=400&h=300&fit=crop&auto=format',
        'Rhinestone Application': 'https://images.unsplash.com/photo-1604654894610-df63bc536371?w=400&h=300&fit=crop&auto=format',
        'Gel Removal': 'https://images.unsplash.com/photo-1567721913486-6585f069b332?w=400&h=300&fit=crop&auto=format',
        'Acrylic Removal': 'https://images.unsplash.com/photo-1567721913486-6585f069b332?w=400&h=300&fit=crop&auto=format',

        # Lash Services
        'Classic Lash Extensions': 'https://images.unsplash.com/photo-1587614382346-4ec70e388b28?w=400&h=300&fit=crop&auto=format',
        'Volume Lash Extensions': 'https://images.unsplash.com/photo-1580870069867-74c57ee1bb07?w=400&h=300&fit=crop&auto=format',
        'Hybrid Lash Extensions': 'https://images.unsplash.com/photo-1585652757141-bf4a4aa786c0?w=400&h=300&fit=crop&auto=format',
        'Mega Volume Lashes': 'https://images.unsplash.com/photo-1588681664899-f142ff2dc9b1?w=400&h=300&fit=crop&auto=format',
        'Lash Lift': 'https://images.unsplash.com/photo-1581342748008-aac7a5a6712a?w=400&h=300&fit=crop&auto=format',
        'Lash Tint': 'https://images.unsplash.com/photo-1542068829-1115f0b7c4ae?w=400&h=300&fit=crop&auto=format',
        'Lash Lift + Tint': 'https://images.unsplash.com/photo-1581342748008-aac7a5a6712a?w=400&h=300&fit=crop&auto=format',
        'Lash Extension Refill (2 weeks)': 'https://images.unsplash.com/photo-1587614382346-4ec70e388b28?w=400&h=300&fit=crop&auto=format',
        'Lash Extension Refill (3 weeks)': 'https://images.unsplash.com/photo-1587614382346-4ec70e388b28?w=400&h=300&fit=crop&auto=format',
        'Lash Extension Removal': 'https://images.unsplash.com/photo-1585652757141-bf4a4aa786c0?w=400&h=300&fit=crop&auto=format',
        'Lower Lash Extensions': 'https://images.unsplash.com/photo-1588681664899-f142ff2dc9b1?w=400&h=300&fit=crop&auto=format',
        'Colored Lash Extensions': 'https://images.unsplash.com/photo-1580870069867-74c57ee1bb07?w=400&h=300&fit=crop&auto=format',

        # Eyebrow Services
        'Eyebrow Shaping': 'https://images.unsplash.com/photo-1604654894610-df63bc536371?w=400&h=300&fit=crop&auto=format',
        'Eyebrow Waxing': 'https://images.unsplash.com/photo-1580618672591-eb180b1a973f?w=400&h=300&fit=crop&auto=format',
        'Eyebrow Threading': 'https://images.unsplash.com/photo-1581342748008-aac7a5a6712a?w=400&h=300&fit=crop&auto=format',
        'Eyebrow Tinting': 'https://images.unsplash.com/photo-1542068829-1115f0b7c4ae?w=400&h=300&fit=crop&auto=format',
        'Eyebrow Lamination': 'https://images.unsplash.com/photo-1585652757141-bf4a4aa786c0?w=400&h=300&fit=crop&auto=format',
        'Henna Brows': 'https://images.unsplash.com/photo-1588681664899-f142ff2dc9b1?w=400&h=300&fit=crop&auto=format',
        'Microblading': 'https://images.unsplash.com/photo-1580870069867-74c57ee1bb07?w=400&h=300&fit=crop&auto=format',
    }
    
    # Return the specific image for the service, or a default based on category
    if service.name in service_images:
        return service_images[service.name]
    
    # Fallback images based on category
    category_name = service.category.name.lower()
    if 'nail' in category_name:
        return 'https://images.unsplash.com/photo-1604654894610-df63bc536371?w=400&h=300&fit=crop&auto=format'
    elif 'lash' in category_name:
        return 'https://images.unsplash.com/photo-1587614382346-4ec70e388b28?w=400&h=300&fit=crop&auto=format'
    elif 'brow' in category_name:
        return 'https://images.unsplash.com/photo-1580618672591-eb180b1a973f?w=400&h=300&fit=crop&auto=format'
    else:
        return 'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=400&h=300&fit=crop&auto=format'