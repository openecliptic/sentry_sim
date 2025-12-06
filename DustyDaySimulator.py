import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# =========================================================================
# Sentry Node Advanced Physics Engine (Corrected Geometry)
# Developed by: Martin Weysi (Ecliptic)
# =========================================================================

def calculate_sun_position(hour, day_of_year=172, lat=30.0): # Day 172 = Summer Solstice (Longest Day)
    """محاسبه موقعیت خورشید"""
    declination = 23.45 * np.sin(np.deg2rad(360/365 * (day_of_year - 81)))
    hour_angle = 15 * (hour - 12)
    
    # ارتفاع خورشید (Elevation)
    elevation = np.rad2deg(np.arcsin(
        np.sin(np.deg2rad(lat)) * np.sin(np.deg2rad(declination)) + 
        np.cos(np.deg2rad(lat)) * np.cos(np.deg2rad(declination)) * np.cos(np.deg2rad(hour_angle))
    ))
    elevation = max(0.1, elevation) # جلوگیری از تقسیم بر صفر
    
    # آزیموت خورشید (برای محاسبه دقیق زاویه برخورد)
    azimuth = np.rad2deg(np.arccos(
        (np.sin(np.deg2rad(declination)) * np.cos(np.deg2rad(lat)) - np.cos(np.deg2rad(declination)) * np.sin(np.deg2rad(lat)) * np.cos(np.deg2rad(hour_angle))) /
        np.cos(np.deg2rad(elevation))
    ))
    return elevation, azimuth

def calculate_iam(incidence_angle):
    """مدل تلفات بازتابی (IAM)"""
    a_r = 0.16 
    theta = np.deg2rad(incidence_angle)
    # محدود کردن زاویه برای جلوگیری از خطای عددی در فرمول IAM
    theta = np.clip(theta, 0, np.deg2rad(85))
    iam = 1 - a_r * (1/np.cos(theta) - 1)
    iam = np.clip(iam, 0, 1)
    return iam

def run_final_simulation():
    print("--- Running Sentry Final Simulation (With Geometric Gain) ---")
    time_steps = np.linspace(5.5, 19.5, 900) # طول روز تابستانی
    amb_temp_base = 35 # دمای محیط گرم تابستان
    
    p_grid_fixed = []
    p_grid_sentry = []
    temp_cell_log = []
    soiling_log = []
    angle_loss_log = []
    
    current_soiling = 0.05 # شروع روز با 5% خاک (واقع‌گرایانه)
    sentry_cleaning_state = False
    cleaning_timer = 0
    
    total_energy_fixed = 0
    total_energy_sentry = 0

    # پارامترهای سیستم ثابت
    tilt_fixed = 30 # زاویه نصب پنل ثابت
    azimuth_fixed = 0 # رو به جنوب

    for i, t in enumerate(time_steps):
        sun_elev, sun_azim = calculate_sun_position(t)
        
        # 1. محاسبه تابش مستقیم نرمال (DNI)
        # فرض: آسمان صاف کویر (DNI بالا)
        if sun_elev > 0:
            dni = 1000 * np.sin(np.deg2rad(sun_elev)) ** 0.15 # مدل ساده شده DNI
            # ابر گذرا
            if 13 < t < 14: 
                dni *= (1.0 - (0.7 * np.abs(np.sin(t * 10))))
        else:
            dni = 0
            
        # 2. محاسبه زاویه برخورد (Incidence Angle)
        # الف) برای سیستم ثابت:
        # فرمول هندسی دقیق زاویه بین خورشید و پنل ثابت
        inc_angle_fixed = np.rad2deg(np.arccos(
            np.sin(np.deg2rad(sun_elev)) * np.cos(np.deg2rad(tilt_fixed)) + 
            np.cos(np.deg2rad(sun_elev)) * np.sin(np.deg2rad(tilt_fixed)) * np.cos(np.deg2rad(sun_azim - azimuth_fixed))
        ))
        
        # ب) برای سیستم Sentry (ترکر):
        inc_angle_sentry = 0 # همیشه عمود
        
        # 3. محاسبه تابش روی سطح پنل (POA - Plane of Array)
        # قانون کسینوس: شدت نور = DNI * cos(theta)
        poa_fixed = dni * np.cos(np.deg2rad(inc_angle_fixed))
        poa_fixed = max(0, poa_fixed) # منفی نشه
        
        poa_sentry = dni * np.cos(np.deg2rad(inc_angle_sentry)) # cos(0) = 1
        
        # 4. سایر تلفات
        iam_fixed = calculate_iam(inc_angle_fixed)
        iam_sentry = 1.0 # اپتیک کامل
        
        # مدل گرد و غبار (تشدید شده برای نمایش اثر)
        dust_event = 0.0003 * (1 + 0.5*np.random.random()) # طوفان خاک
        current_soiling += dust_event
        
        # منطق تمیزکاری Sentry
        sentry_soiling = current_soiling
        if sentry_soiling > 0.08 and poa_sentry > 300 and cleaning_timer == 0:
            cleaning_timer = 30
            current_soiling = 0.005 # تمیز شد
        if cleaning_timer > 0: cleaning_timer -= 1
        
        # 5. دمای سلول (NOCT)
        t_cell = amb_temp_base + (poa_sentry / 800) * (45 - 20) # فرض بدترین دما (دمای sentry که بیشتره)
        thermal_eff = 1 - 0.004 * (t_cell - 25)
        
        # 6. محاسبه توان نهایی
        p_rated = 400 * 20
        
        # توان ثابت (بدون تمیزکاری، زاویه غلط)
        # توجه: current_soiling برای سیستم ثابت کم نمیشه
        # برای شبیه‌سازی دقیق‌تر، باید دو تا متغیر خاک جدا داشته باشیم
        # اینجا فرض میکنیم Sentry تمیز میکنه ولی Fixed کثیف میمونه
        # پس باید مقدار خاک رو برای Sentry جدا کنیم
        
        # اصلاح منطق خاک:
        # خاک سیستم ثابت همینجوری زیاد میشه
        soiling_fixed = min(0.4, 0.05 + (i * 0.0003)) # خاک خطی زیاد میشه تا 40%
        # خاک سیستم Sentry
        soiling_sentry = 0.005 if cleaning_timer > 0 else (sentry_soiling if sentry_soiling < 0.1 else 0.005) # ساده‌سازی برای گراف
        
        # استفاده از soiling_log برای نمایش درست
        # بذارید متغیر رو درست کنم که گراف خاک هم درست دربیاد
        # همون current_soiling رو برای Sentry نگه میداریم و Fixed رو جدا میسازیم
        
        pow_fixed = p_rated * (poa_fixed/1000) * thermal_eff * iam_fixed * (1 - soiling_fixed)
        pow_sentry = p_rated * (poa_sentry/1000) * thermal_eff * iam_sentry * (1 - current_soiling)
        
        if pow_fixed < 0: pow_fixed = 0
        if pow_sentry < 0: pow_sentry = 0
        
        p_grid_fixed.append(pow_fixed)
        p_grid_sentry.append(pow_sentry)
        soiling_log.append(current_soiling * 100)
        angle_loss_log.append((1 - np.cos(np.deg2rad(inc_angle_fixed))) * 100) # تلفات هندسی
        temp_cell_log.append(t_cell)
        
        total_energy_fixed += pow_fixed 
        total_energy_sentry += pow_sentry 

    gain_percentage = ((total_energy_sentry/total_energy_fixed)-1)*100

    # ================== رسم نمودار ==================
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(14, 12))
    gs = gridspec.GridSpec(3, 2, height_ratios=[2.5, 1, 0.8])

    # 1. Main Power Plot
    ax1 = plt.subplot(gs[0, :])
    ax1.plot(time_steps, np.array(p_grid_sentry)/1000, color='#00ff99', linewidth=3, label='Sentry Node (Tracker + AI Clean)')
    ax1.plot(time_steps, np.array(p_grid_fixed)/1000, color='#ff6b6b', linestyle='--', linewidth=2, label='Fixed System (Static + Dirty)')
    ax1.fill_between(time_steps, np.array(p_grid_fixed)/1000, np.array(p_grid_sentry)/1000, color='#00ff99', alpha=0.2)
    
    ax1.text(13.5, 2, 'Cloud Event', color='white', ha='center', bbox=dict(facecolor='gray', alpha=0.5))
    ax1.set_ylabel('Power (kW)', fontsize=12, color='white')
    ax1.set_title('Sentry System Performance Analysis (Summer Dust Storm)', fontsize=16, fontweight='bold', pad=15)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.2)
    
    # 2. Geometric Loss Plot
    ax2 = plt.subplot(gs[1, 0])
    ax2.plot(time_steps, angle_loss_log, color='#ffcc00', linewidth=2)
    ax2.fill_between(time_steps, 0, angle_loss_log, color='#ffcc00', alpha=0.2)
    ax2.set_ylabel('Geometric Loss (%)', fontsize=10)
    ax2.set_title('Cosine Efficiency Loss (Fixed Panel)', fontsize=12, color='#ffcc00')
    ax2.grid(True, alpha=0.2)
    
    # 3. Soiling Plot
    ax3 = plt.subplot(gs[1, 1])
    ax3.plot(time_steps, soiling_log, color='#ff99cc', linewidth=2)
    ax3.set_ylabel('Dust Level (%)', fontsize=10)
    ax3.set_title('Soiling Accumulation & AI Cleaning', fontsize=12, color='#ff99cc')
    ax3.grid(True, alpha=0.2)

    # 4. Thermal Plot
    ax4 = plt.subplot(gs[2, :])
    ax4.plot(time_steps, temp_cell_log, color='orange', linewidth=2)
    ax4.set_ylabel('Cell Temp (°C)', fontsize=10)
    ax4.set_title('Panel Temperature', fontsize=12, color='white')
    ax4.grid(True, alpha=0.2)

    # Result Box
    fig.text(0.5, 0.02, f"TOTAL ENERGY GAIN: +{gain_percentage:.1f}%", ha='center', fontsize=26, color='#00ff99', weight='bold', bbox=dict(facecolor='black', edgecolor='#00ff99', boxstyle='round,pad=0.5'))

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.1)
    plt.show()

if __name__ == "__main__":
    run_final_simulation()