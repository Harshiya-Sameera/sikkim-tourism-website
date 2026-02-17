from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from portal import views as portal_views
from tourism import views as tourism_views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Landing & Core Pages
    path('', portal_views.landing_view, name='landing'),

    # Tourism / Explore
    path('tourism/', tourism_views.ExplorePlacesView.as_view(), name='explore_places'),
    path('tourism/place/<int:pk>/', tourism_views.place_detail_view, name='place_detail'),

    # Optional clean alias (UI-friendly)
    path('explore/', tourism_views.ExplorePlacesView.as_view(), name='explore'),
    path('categories/', portal_views.categories_view, name='categories'),
    path('recognition/', portal_views.api_extract_image, name='ai_lens_api'),
    path('ai-lens/', portal_views.ai_lens_view, name='ai_lens'),
    path('itinerary/', portal_views.itinerary_view, name='itinerary'),
    path('api/places-geojson/', portal_views.places_geojson, name='places_geojson'),
    path('map/', portal_views.map_view, name='interactive_map'),
    path('admin-panel/bulk-upload/', portal_views.bulk_upload_places, name='admin_bulk_upload'),

    # User
    path('dashboard/', portal_views.user_dashboard_view, name='user_dashboard'),
    path('profile/', portal_views.profile_settings_view, name='profile_settings'),

    # Admin Panel
    path('admin-panel/', portal_views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-panel/users/', portal_views.user_directory_view, name='admin_user_management'),
    path('admin-panel/analytics/', portal_views.admin_analytics_view, name='admin_analytics'),
    path('admin-panel/ai-core/', portal_views.ai_monitor_view, name='admin_ai_monitor'),
    path('admin-panel/content/', portal_views.manage_places_view, name='admin_manage_places'),
    path('admin-panel/content/delete/<int:pk>/', portal_views.delete_place, name='delete_place'),
    path('admin-panel/chat-logs/', portal_views.admin_chat_logs_view, name='admin_chat_logs'),
    path('admin-panel/users/toggle/<int:user_id>/', portal_views.toggle_user_status, name='toggle_user_status'),
    path('admin-panel/users/delete/<int:user_id>/', portal_views.delete_explorer, name='delete_explorer'),
    path('itinerary/view/<int:plan_id>/', portal_views.view_plan_detail, name='view_plan'),

    # Chatbot
    path('chatbot/', include('chatbot.urls')),

    # Auth
    path('accounts/', include('accounts.urls')),
]

# Static & Media (DEV only)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
