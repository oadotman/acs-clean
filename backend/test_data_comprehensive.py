"""
Comprehensive Test Data for Platform-Specific Ad Generation
Covers all platforms with various ad types and edge cases
"""

# Test data organized by platform and test case type
PLATFORM_TEST_DATA = {
    'facebook': {
        'short_ads': [
            "Buy now!",
            "Amazing deals today.",
            "Get 50% off everything!"
        ],
        'long_ads': [
            "Transform your business with our revolutionary AI-powered marketing platform. Join thousands of successful entrepreneurs who have already doubled their revenue using our proven strategies. Don't miss out on this limited-time opportunity to scale your business like never before.",
            "Discover the secret to perfect ad copy that converts. Our comprehensive training program includes step-by-step tutorials, real-world case studies, and one-on-one coaching sessions. Learn from industry experts who have generated millions in revenue through optimized advertising campaigns.",
            "Looking for the best fitness equipment for your home gym? Our premium collection features professional-grade machines at affordable prices. Free delivery, expert setup, and lifetime warranty included. Transform your body and your life starting today."
        ],
        'no_cta_ads': [
            "Our new product launch was incredibly successful.",
            "We've been helping businesses grow for over 20 years.",
            "The reviews are amazing and customers love our service."
        ],
        'multiple_cta_ads': [
            "Buy now and save 30%! Click here to shop. Don't wait, order today! Call us now!",
            "Sign up for free trial. Download the app. Subscribe to premium. Get started immediately!",
            "Book your consultation. Schedule a demo. Contact our team. Apply today!"
        ],
        'poor_grammar_ads': [
            "best product ever you will love it so much buy now dont wait",
            "We has the most amazing deals for you today! Dont miss out this opportunity to save big money!",
            "Are business need more customer? We help you get lot of sales very quick!"
        ],
        'well_written_ads': [
            "Unlock your business potential with our award-winning marketing automation platform. Join 50,000+ entrepreneurs who've increased their ROI by 300%. Start your free 14-day trial today.",
            "Transform your fitness journey with personalized workout plans designed by certified trainers. See results in just 30 days or your money back. Download the app now.",
            "Discover handcrafted jewelry that tells your unique story. Each piece is meticulously designed using ethically sourced materials. Shop our exclusive collection today."
        ],
        'edge_cases': [
            "🔥🔥🔥 SALE 🔥🔥🔥 Everything must go!!! 90% OFF!!!",
            "Product name: SuperWidget Pro 3000. Features: Advanced AI, Cloud Integration, Real-time Analytics. Price: $99.99/month. Special offer: 3 months free.",
            ""  # Empty ad
        ]
    },
    
    'instagram': {
        'short_ads': [
            "✨ New drop ✨",
            "Weekend vibes only 💙",
            "Your glow up starts here ⭐"
        ],
        'long_ads': [
            "Swipe left to see the transformation! 💫 Our skincare routine helped Sarah achieve glass skin in just 30 days. The secret? Clean ingredients, proven results, and a community that supports your journey. Ready to glow like never before?",
            "From struggling entrepreneur to 7-figure business owner 🚀 Here's my story and the 3 game-changing strategies that made all the difference. Save this post and implement these tips to transform your business today. Which tip resonates most with you?",
            "Morning coffee tastes better when you know you're making a difference ☕ Every bag sold provides clean water to families in need. Premium quality, ethical sourcing, positive impact. That's what we call the perfect blend."
        ],
        'no_cta_ads': [
            "Behind the scenes of our photo shoot today 📸",
            "Grateful for this beautiful sunset moment 🌅",
            "Team meeting vibes - planning something amazing ✨"
        ],
        'multiple_cta_ads': [
            "Tag a friend! Share this post! Save for later! Comment below! DM us now!",
            "Swipe left! Click the link! Follow us! Turn on notifications! Shop now!",
            "Double tap if you agree! Share your story! Tag us in your post! Use our hashtag!"
        ],
        'poor_grammar_ads': [
            "best products ever you will love them so much dm us now",
            "We has the most amazing cloths! Dont miss out this sale very good price!",
            "Are you need more followers? We help you get lot of likes very quick!"
        ],
        'well_written_ads': [
            "That post-workout glow hits different ✨ Fuel your fitness journey with our plant-based protein blend. Clean ingredients, amazing taste, real results. Link in bio to start your transformation 💪",
            "Plot twist: Self-care isn't selfish 🛁 Treat yourself to our luxury spa experience at home. Hand-selected essential oils meet organic botanicals. Because you deserve moments of pure bliss ✨",
            "Small business owner life: 3am ideas, coffee-fueled dreams, and the courage to build something beautiful 🌟 Supporting small means supporting dreams. Thank you for being part of our story 💕"
        ],
        'edge_cases': [
            "Check out our new product with absolutely no hashtags at all",
            "#sale #discount #buy #now #limited #time #offer #best #deal #ever #shop #today #save #money #quality #products #free #shipping #satisfaction #guaranteed #customer #service #reviews #testimonials #success #stories #transformation #results #proven #effective #premium #luxury #affordable #budget #friendly",  # Too many hashtags
            "🔥💥⚡✨🌟💫⭐🎯🚀💎🏆🎉🎊🔥💥⚡✨🌟💫⭐🎯🚀💎🏆🎉🎊"  # Only emojis
        ]
    },
    
    'google_ads': {
        'short_ads': [
            "Buy now.",
            "Best deals.",
            "Save today!"
        ],
        'long_ads': [
            "Professional marketing services that deliver real results for your business. Our expert team specializes in digital advertising campaigns that increase your online visibility and drive qualified leads to your website.",
            "Transform your home with our premium furniture collection featuring modern designs, sustainable materials, and unbeatable prices. Free delivery and white-glove setup service included with every purchase.",
            "Learn digital marketing from industry experts through our comprehensive online course. Master SEO, PPC, social media marketing, and analytics with hands-on projects and personalized feedback."
        ],
        'no_cta_ads': [
            "We provide excellent customer service.",
            "Our company has been in business for 25 years.",
            "Quality products at competitive prices."
        ],
        'multiple_cta_ads': [
            "Call now! Visit our website! Download our app! Schedule a consultation! Get your free quote!",
            "Shop now! Subscribe today! Join our newsletter! Follow us! Share with friends!",
            "Book appointment! Request demo! Start free trial! Contact sales! Learn more!"
        ],
        'poor_grammar_ads': [
            "we has best service you will love dont wait call now",
            "Are business need more customer we help get sales quick",
            "best product for you buy now very good price dont miss"
        ],
        'well_written_ads': [
            "Boost your online presence with our proven digital marketing strategies. Increase leads by 250% in 90 days. Free consultation available.",
            "Premium kitchen appliances that make cooking effortless. Energy-efficient, stylish designs with 5-year warranty. Shop now and save 30%.",
            "Master Python programming with our interactive online course. Built by industry experts, perfect for beginners. Start your coding journey today."
        ],
        'edge_cases': [
            "Get results.",  # Very minimal - single sentence
            "Marketing Services | SEO | PPC | Social Media | Content | Analytics | Consulting | Training | Strategy | Results",  # Pipe-separated format
            "Product Features: A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z"  # Very long feature list
        ]
    },
    
    'linkedin': {
        'short_ads': [
            "Advance your career today.",
            "Professional networking made easy.",
            "Leadership training available."
        ],
        'long_ads': [
            "Accelerate your career with our executive leadership program designed for ambitious professionals. Learn from Fortune 500 CEOs, develop strategic thinking skills, and build a powerful network that opens doors to new opportunities.",
            "Transform your business operations with our comprehensive digital transformation consulting services. Our experienced consultants help enterprise clients modernize their systems, optimize workflows, and achieve measurable ROI.",
            "Join thousands of professionals who have advanced their careers through our industry-leading certification programs. Expert-led training, practical case studies, and career placement assistance included."
        ],
        'no_cta_ads': [
            "Our team recently completed a successful project implementation.",
            "We're proud to announce our partnership with industry leaders.",
            "Celebrating 10 years of innovation and client success."
        ],
        'multiple_cta_ads': [
            "Connect with us! Schedule a demo! Download our whitepaper! Join our webinar! Request consultation!",
            "Follow our company! Share this post! Comment your thoughts! Send us a message! Book a call!",
            "Register now! Apply today! Learn more! Get started! Contact our team!"
        ],
        'poor_grammar_ads': [
            "we has best solution for you business growth call us now",
            "Are company need more leads we help get customers quick",
            "professional service very good price for business owner dont wait"
        ],
        'well_written_ads': [
            "Streamline your hiring process with our AI-powered talent acquisition platform. Reduce time-to-hire by 60% while finding the perfect candidates. Request a personalized demo today.",
            "Drive innovation in your organization with our design thinking workshops. Led by certified facilitators, these interactive sessions transform how your team approaches problem-solving.",
            "Expand your global reach with our international business development services. Navigate complex markets, establish strategic partnerships, and achieve sustainable growth worldwide."
        ],
        'edge_cases': [
            "B2B SaaS CRM ERP ROI KPI API SDK CTO CEO CFO CMO VP SVP Director Manager",  # Business acronym heavy
            "Enterprise solution for enterprise clients requiring enterprise-level support and enterprise integration capabilities.",  # Repetitive enterprise language
            "Thought leadership executive strategic synergy paradigm shift best practices core competencies value proposition"  # Corporate buzzword heavy
        ]
    },
    
    'twitter_x': {
        'short_ads': [
            "🚀 New launch!",
            "Game changer 💪",
            "Must have! ⭐"
        ],
        'long_ads': [
            "THREAD: How I went from $0 to $100k in 12 months 🧵 The strategies nobody talks about, the mistakes that almost killed my business, and the one pivot that changed everything. Buckle up 👇",
            "Breaking: New study reveals 90% of startups fail because of this ONE mistake. We analyzed 10,000 companies and the results will shock you. Here's what successful founders do differently 🔥",
            "Plot twist: The best marketing advice I ever received came from a 10-year-old. Sometimes the most powerful insights come from the most unexpected places. Here's what she taught me about authenticity 💡"
        ],
        'no_cta_ads': [
            "Just finished an amazing coffee meeting with the team.",
            "Grateful for all the positive feedback from our users today.",
            "Beautiful sunset from the office window this evening."
        ],
        'multiple_cta_ads': [
            "RT this! Like if you agree! Comment below! Follow for more! DM for details!",
            "Share your story! Tag a friend! Join the conversation! Click the link! Subscribe now!",
            "Retweet to win! Follow us! Turn on notifications! Reply with your answer! Check our bio!"
        ],
        'poor_grammar_ads': [
            "we has best product you will love it buy now dont wait",
            "are you need more followers we help get lot of engagement quick",
            "best service for business owner very good price call now"
        ],
        'well_written_ads': [
            "That moment when your product finally clicks for users 🎯 3 years of iteration, countless user interviews, and pure determination. The journey was worth it. What's your biggest product breakthrough? 🚀",
            "Hot take: Most productivity advice is garbage 🗑️ Instead of adding more tools, try removing distractions. I deleted 47 apps and my focus increased 300%. Sometimes less really is more ✨",
            "Customer just said our app 'changed their life' 🥺 Moments like these remind me why we do what we do. Building products that matter > chasing vanity metrics. Always. 💪"
        ],
        'edge_cases': [
            "a" * 280,  # Exactly 280 characters
            "🐦🔥💯⚡✨🚀💪🎯🌟💎🏆🎉🔥💯⚡✨🚀💪🎯🌟💎🏆🎉🔥💯⚡✨🚀💪🎯🌟💎🏆🎉🔥💯⚡✨🚀💪🎯🌟💎🏆🎉🔥💯⚡✨🚀💪🎯🌟💎🏆🎉",  # Emoji heavy
            "@user1 @user2 @user3 @user4 @user5 #hashtag1 #hashtag2 #hashtag3 #hashtag4 #hashtag5 Check this out!"  # Heavy mentions and hashtags
        ]
    },
    
    'tiktok': {
        'short_ads': [
            "POV: You found the hack ✨",
            "This changed everything 🤯",
            "Wait for it... 👀"
        ],
        'long_ads': [
            "Day 1 of trying this viral life hack that everyone's talking about and OMG I can't believe the results! If you've been struggling with the same problem, this might be the solution you've been looking for. Trust the process!",
            "Storytime: How a random TikTok comment literally changed my entire business strategy and led to 6-figure revenue in 3 months. Sometimes the best advice comes from the most unexpected places. Here's what happened...",
            "Rating viral productivity hacks so you don't have to! Spent 30 days testing every trend and these are the results. Some will shock you, others will save you hours. Which one surprised you most?"
        ],
        'no_cta_ads': [
            "Just vibing with my morning routine today",
            "Behind the scenes of content creation life",
            "Grateful for this community and all your support"
        ],
        'multiple_cta_ads': [
            "Follow for more! Like this video! Share with friends! Comment your thoughts! Save this post!",
            "Try this hack! Tag someone! Duet this! Stitch your response! Turn on notifications!",
            "Rate this 1-10! Tell me in comments! Share your story! Follow if you relate! DM me!"
        ],
        'poor_grammar_ads': [
            "this hack will change you life trust me try it now",
            "are you tired of being tired this product help you feel better quick",
            "best trend ever you will love it so much follow for more"
        ],
        'well_written_ads': [
            "POV: You discovered the morning routine that actually works ☀️ No more 5am wake-ups or complicated rituals. Just 3 simple steps that transformed my entire day. Ready to try it?",
            "That satisfying moment when you finally organize your entire life 📱✨ From chaos to clarity in just one weekend. Here's exactly how I did it and how you can too!",
            "Plot twist: The best skincare routine costs under $20 🤯 Dermatologists hate this simple 3-step method but the results speak for themselves. Your future skin will thank you!"
        ],
        'edge_cases': [
            "#fyp #foryou #viral #trending #hack #life #tips #advice #motivation #inspiration #success #mindset #goals #dreams #hustle #grind #work #business #entrepreneur #lifestyle",  # Hashtag heavy
            "This. Is. How. You. Get. Maximum. Impact. With. Minimal. Effort.",  # Period separated for emphasis
            "✨🔥💯⚡🌟💫⭐🎯🚀💎🏆🎉🎊💖🤩😍🥳🤯😱🙌👏💪🔥✨💯⚡🌟💫"  # Emoji overload
        ]
    }
}

# Expected parsing results for validation
EXPECTED_PARSING_RESULTS = {
    'facebook': {
        'required_fields': ['headline', 'body', 'cta'],
        'optional_fields': [],
        'max_lengths': {'headline': 125, 'body': 500, 'cta': 20}
    },
    'instagram': {
        'required_fields': ['body'],
        'optional_fields': ['hashtags', 'cta'],
        'max_lengths': {'body': 2200, 'hashtags': 30, 'cta': 20}
    },
    'google_ads': {
        'required_fields': ['headlines', 'descriptions'],
        'optional_fields': ['cta'],
        'max_lengths': {'headlines': 30, 'descriptions': 90, 'cta': 20}
    },
    'linkedin': {
        'required_fields': ['headline', 'body', 'cta'],
        'optional_fields': [],
        'max_lengths': {'headline': 150, 'body': 600, 'cta': 20}
    },
    'twitter_x': {
        'required_fields': ['body'],
        'optional_fields': [],
        'max_lengths': {'body': 280}
    },
    'tiktok': {
        'required_fields': ['body'],
        'optional_fields': ['cta'],
        'max_lengths': {'body': 300, 'cta': 20}
    }
}

# Quality validation criteria
QUALITY_CRITERIA = {
    'forbidden_templates': [
        'Transform your',
        'Discover the secret',
        'Unlock your potential',
        'Join thousands of',
        'Don\'t miss out',
        'Limited time offer',
        'Act now',
        'Call now',
        'Click here',
        'Learn more'
    ],
    'grammar_issues': [
        'you will love it so much',
        'very good price',
        'dont wait',
        'we has',
        'are you need',
        'lot of'
    ],
    'minimum_confidence_score': 60,
    'maximum_confidence_score': 100
}

def get_test_ads_for_platform(platform_id: str):
    """Get all test ads for a specific platform"""
    return PLATFORM_TEST_DATA.get(platform_id, {})

def get_all_test_ads():
    """Get all test ads across all platforms"""
    return PLATFORM_TEST_DATA

def get_parsing_expectations(platform_id: str):
    """Get expected parsing results for platform validation"""
    return EXPECTED_PARSING_RESULTS.get(platform_id, {})

def get_quality_criteria():
    """Get quality validation criteria"""
    return QUALITY_CRITERIA