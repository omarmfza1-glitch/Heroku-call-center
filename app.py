"""
Smart Call Center - Heroku Version - Fixed Audio
مركز الاتصال الذكي - نسخة Heroku محدثة للصوت
"""

from flask import Flask, request, Response
import os
import logging

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/twilio/voice", methods=['POST', 'GET'])
def handle_twilio_voice():
    """معالجة مكالمات Twilio مع تحسينات الصوت"""
    
    try:
        logger.info("🎯 === TWILIO VOICE WEBHOOK START ===")
        logger.info(f"Request Method: {request.method}")
        logger.info(f"Request URL: {request.url}")
        logger.info(f"Request Headers: {dict(request.headers)}")
        logger.info(f"Form Data: {dict(request.form)}")
        
        # التعامل مع GET requests للاختبار
        if request.method == 'GET':
            logger.info("📱 GET request - returning test page")
            return """
            <div style="font-family: Arial; text-align: center; padding: 30px;">
                <h1>✅ Twilio Voice Webhook يعمل!</h1>
                <p style="color: green; font-size: 20px;">✅ Heroku Server: Online</p>
                <p><strong>Webhook URL:</strong> /twilio/voice</p>
                <p><strong>Method Required:</strong> POST</p>
                <p><strong>Status:</strong> Ready for calls 📞</p>
            </div>
            """
        
        # الحصول على معلومات المكالمة
        call_sid = request.form.get('CallSid', 'unknown')
        from_number = request.form.get('From', 'unknown')
        to_number = request.form.get('To', 'unknown')
        call_status = request.form.get('CallStatus', 'unknown')
        account_sid = request.form.get('AccountSid', 'unknown')
        
        logger.info("📞 === CALL DETAILS ===")
        logger.info(f"Call SID: {call_sid}")
        logger.info(f"From Number: {from_number}")
        logger.info(f"To Number: {to_number}")
        logger.info(f"Call Status: {call_status}")
        logger.info(f"Account SID: {account_sid}")
        
        # التحقق من صحة البيانات
        if not call_sid or call_sid == 'unknown':
            logger.warning("⚠️ Invalid request - missing CallSid")
            return Response("Missing CallSid", status=400)
        
        # تحديد رد مخصص حسب رقم المتصل
        welcome_message = "السلام عليكم ومرحباً بكم في مركز الاتصال الذكي"
        
        if from_number and from_number != 'unknown':
            if '+966' in from_number:
                welcome_message = "أهلاً وسهلاً بك من المملكة العربية السعودية في مركز الاتصال الذكي"
            elif '+1' in from_number:
                welcome_message = "Welcome to our Smart Call Center. مرحباً بكم في مركز الاتصال الذكي"
        
        # TwiML Response محسن للصوت
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="ar-EG">{welcome_message}</Say>
    <Pause length="2"/>
    <Say voice="alice" language="ar-EG">النظام يعمل على سيرفر هيروكو بنجاح تام</Say>
    <Pause length="1"/>
    <Say voice="alice" language="ar-EG">يرجى البقاء على الخط. سأطلب منكم تسجيل رسالة قصيرة</Say>
    <Pause length="1"/>
    <Say voice="alice" language="ar-EG">بعد سماع الصوت، تحدثوا لمدة عشر ثوانٍ</Say>
    <Record action="/twilio/recording" method="POST" maxLength="10" playBeep="true" timeout="3" transcribe="false"/>
    <Say voice="alice" language="ar-EG">شكراً لكم على التسجيل</Say>
    <Pause length="1"/>
    <Say voice="alice" language="ar-EG">تم استلام رسالتكم بنجاح وسيتم الرد عليكم قريباً</Say>
    <Pause length="1"/>
    <Say voice="alice" language="ar-EG">نشكركم لاتصالكم بنا. مع السلامة</Say>
    <Hangup/>
</Response>'''
        
        logger.info("✅ === SENDING TWIML RESPONSE ===")
        logger.info("TwiML Response:")
        logger.info(twiml)
        
        # إنشاء Response مع headers محددة
        response = Response(twiml, mimetype='text/xml')
        response.headers['Content-Type'] = 'text/xml; charset=utf-8'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        logger.info("📤 TwiML response sent successfully")
        return response
        
    except Exception as e:
        logger.error(f"❌ ERROR in voice handler: {str(e)}")
        logger.error(f"❌ Exception type: {type(e).__name__}")
        
        # رد طارئ بسيط جداً
        emergency_twiml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="en">Hello. This is Smart Call Center. System error occurred. Thank you for calling.</Say>
    <Hangup/>
</Response>'''
        
        logger.info("📤 Sending emergency TwiML")
        return Response(emergency_twiml, mimetype='text/xml')

@app.route("/twilio/recording", methods=['POST'])
def handle_twilio_recording():
    """معالجة التسجيلات الصوتية"""
    
    try:
        logger.info("🎤 === RECORDING WEBHOOK START ===")
        logger.info(f"Form Data: {dict(request.form)}")
        
        call_sid = request.form.get('CallSid', 'unknown')
        recording_url = request.form.get('RecordingUrl', '')
        recording_duration = request.form.get('RecordingDuration', '0')
        recording_sid = request.form.get('RecordingSid', 'unknown')
        
        logger.info(f"🎤 Call SID: {call_sid}")
        logger.info(f"🎤 Recording SID: {recording_sid}")
        logger.info(f"🎤 Recording URL: {recording_url}")
        logger.info(f"🎤 Recording Duration: {recording_duration} seconds")
        
        # تحليل مدة التسجيل
        duration = int(recording_duration) if recording_duration.isdigit() else 0
        
        if duration == 0:
            response_text = "لم نستلم تسجيل صوتي. لا بأس، شكراً لاتصالكم"
        elif duration < 3:
            response_text = "استلمنا تسجيل قصير. شكراً لكم"
        elif duration < 8:
            response_text = "تم استلام رسالتكم الصوتية بنجاح. شكراً لكم"
        else:
            response_text = "تم استلام رسالتكم الطويلة بنجاح. سيتم مراجعتها والرد عليكم قريباً"
        
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="ar-EG">{response_text}</Say>
    <Pause length="2"/>
    <Say voice="alice" language="ar-EG">نقدر لكم الوقت الذي أمضيتموه معنا</Say>
    <Pause length="1"/>
    <Say voice="alice" language="ar-EG">مع السلامة</Say>
    <Hangup/>
</Response>'''
        
        logger.info("✅ Recording response sent")
        
        return Response(twiml, mimetype='text/xml')
        
    except Exception as e:
        logger.error(f"❌ ERROR in recording handler: {str(e)}")
        
        simple_response = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="ar-EG">شكراً لكم</Say>
    <Hangup/>
</Response>'''
        
        return Response(simple_response, mimetype='text/xml')

@app.route("/twilio/status", methods=['POST'])
def handle_twilio_status():
    """معالجة حالة المكالمة"""
    
    logger.info("📊 === CALL STATUS WEBHOOK ===")
    logger.info(f"Status Form Data: {dict(request.form)}")
    
    call_sid = request.form.get('CallSid', 'unknown')
    call_status = request.form.get('CallStatus', 'unknown')
    call_duration = request.form.get('CallDuration', '0')
    direction = request.form.get('Direction', 'unknown')
    
    logger.info(f"📊 Call SID: {call_sid}")
    logger.info(f"📊 Call Status: {call_status}")
    logger.info(f"📊 Call Duration: {call_duration} seconds")
    logger.info(f"📊 Direction: {direction}")
    
    if call_status == 'completed':
        logger.info("✅ Call completed successfully")
    elif call_status == 'failed':
        logger.error("❌ Call failed")
    elif call_status == 'busy':
        logger.warning("📞 Call was busy")
    elif call_status == 'no-answer':
        logger.warning("📞 No answer")
    elif call_status == 'canceled':
        logger.info("📞 Call was canceled")
    
    return "OK"

@app.route("/test-voice")
def test_voice_direct():
    """اختبار TwiML مباشر"""
    
    logger.info("🧪 Direct voice test requested")
    
    test_twiml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="ar-EG">هذا اختبار مباشر للصوت العربي في النظام</Say>
    <Pause length="2"/>
    <Say voice="alice" language="ar-EG">إذا سمعتم هذه الرسالة فالنظام يعمل بشكل ممتاز</Say>
    <Pause length="1"/>
    <Say voice="alice" language="en">This is a direct voice test. If you hear this, the system is working perfectly.</Say>
</Response>'''
    
    return Response(test_twiml, mimetype='text/xml')

@app.route("/test")
def test_page():
    """صفحة اختبار النظام"""
    
    return """
    <div style="font-family: Arial; text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh;">
        <h1>🧪 اختبار النظام</h1>
        <h2 style="color: #90EE90;">✅ Heroku Server Active!</h2>
        
        <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin: 20px auto; max-width: 600px;">
            <h3 style="color: #FFD700;">📊 System Status:</h3>
            <p>✅ Flask Server: Running</p>
            <p>✅ Heroku Platform: Active</p>
            <p>✅ Twilio Webhooks: Ready</p>
            <p>✅ Voice Processing: Enabled</p>
            <p>✅ Arabic TTS: Configured</p>
        </div>
        
        <div style="margin: 30px;">
            <a href="/twilio/voice" style="background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; margin: 10px; display: inline-block;">📞 Test Voice Webhook</a>
            <a href="/test-voice" style="background: #17a2b8; color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; margin: 10px; display: inline-block;">🎤 Test TwiML Direct</a>
        </div>
        
        <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; margin: 20px auto; max-width: 500px;">
            <h4 style="color: #FFD700;">📞 To test the system:</h4>
            <p style="font-size: 24px; color: #90EE90;">Call: +1 570 525 5521</p>
        </div>
    </div>
    """

@app.route("/")
def home():
    """الصفحة الرئيسية"""
    
    return """
    <div style="font-family: Arial; text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh;">
        <h1 style="font-size: 48px; margin-bottom: 20px;">🎯 مركز الاتصال الذكي</h1>
        <h2 style="color: #90EE90; margin-bottom: 30px;">✅ يعمل على Heroku - Audio Fixed!</h2>
        
        <div style="background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; margin: 30px auto; max-width: 600px; backdrop-filter: blur(10px);">
            <h3 style="color: #FFD700; margin-bottom: 20px;">📞 للاختبار اتصل على:</h3>
            <p style="font-size: 32px; color: #90EE90; font-weight: bold; margin: 20px 0;">+1 570 525 5521</p>
            
            <div style="margin: 30px 0;">
                <h4 style="color: #FFD700;">🎤 الجديد في هذا الإصدار:</h4>
                <ul style="text-align: right; color: #E0E0E0; font-size: 16px;">
                    <li>تحسينات صوتية كبيرة</li>
                    <li>رسائل أوضح وأطول</li>
                    <li>دعم أفضل للغة العربية</li>
                    <li>معالجة أخطاء محسنة</li>
                    <li>تسجيل مفصل للمكالمات</li>
                </ul>
            </div>
        </div>
        
        <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin: 20px auto; max-width: 500px;">
            <h4 style="color: #FFD700;">🔧 حالة النظام:</h4>
            <p>✅ Heroku Server: نشط</p>
            <p>✅ Audio System: محسن</p>
            <p>✅ Arabic Voice: مُحدث</p>
            <p>✅ Error Handling: متقدم</p>
        </div>
        
        <div style="margin: 30px;">
            <a href="/test" style="background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-size: 18px; margin: 10px; display: inline-block;">🧪 اختبار مفصل</a>
            <a href="/test-voice" style="background: #17a2b8; color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-size: 18px; margin: 10px; display: inline-block;">🎤 اختبار الصوت</a>
        </div>
        
        <footer style="margin-top: 50px; color: #B0B0B0;">
            <p>🚀 Powered by Heroku | 🎯 Smart Call Center v3.0 - Audio Enhanced</p>
        </footer>
    </div>
    """

# تشغيل التطبيق
if __name__ == "__main__":
    # الحصول على port من Heroku
    port = int(os.environ.get("PORT", 5000))
    
    print("🚀 Smart Call Center - Heroku Version v3.0")
    print("="*60)
    print("🎤 Audio System: Enhanced")
    print("🌐 Platform: Heroku")
    print(f"📡 Port: {port}")
    print("📞 Voice: Arabic + English")
    print("🔧 Error Handling: Advanced")
    print("="*60)
    print("✅ Ready for Twilio calls!")
    
    # تشغيل التطبيق
    app.run(host="0.0.0.0", port=port, debug=False)
