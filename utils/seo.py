"""SEO utilities for VocalBrand Supreme.

This module provides functions to inject SEO meta tags, structured data,
and tracking codes for search engine optimization and discoverability.
"""
import streamlit as st


def inject_seo_meta():
    """Inject comprehensive SEO meta tags for search engines, social platforms, and AI assistants.
    
    Includes:
    - Standard meta tags (description, keywords, author)
    - Open Graph tags (Facebook, LinkedIn)
    - Twitter Card tags
    - Structured data (JSON-LD) for Google rich results
    - FAQ schema for voice search optimization
    """
    st.markdown("""
    <!-- Primary Meta Tags -->
    <meta name="title" content="VocalBrand Supreme - Clone Your Voice in 30 Seconds | AI Voice Generator" />
    <meta name="description" content="Transform your voice into a digital asset. Clone your voice in 30 seconds and generate unlimited professional audio with AI. 99.9% uptime, under 1.2s generation. Try free - no credit card required!" />
    <meta name="keywords" content="voice cloning, AI voice generator, text to speech, voice synthesis, audio content creation, professional voice cloning, ElevenLabs alternative, AI audio generator, voice AI, speech synthesis, content creator tools" />
    <meta name="author" content="VocalBrand Team" />
    <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1" />
    <meta name="language" content="English" />
    <meta name="revisit-after" content="7 days" />
    <link rel="canonical" href="https://vocalbrand.streamlit.app" />
    
    <!-- Open Graph / Facebook / LinkedIn -->
    <meta property="og:type" content="website" />
    <meta property="og:url" content="https://vocalbrand.streamlit.app/" />
    <meta property="og:title" content="VocalBrand Supreme - AI Voice Cloning in 30 Seconds" />
    <meta property="og:description" content="Transform your voice into a digital asset. Clone once, generate unlimited professional audio. Used by 10,000+ content creators, educators, and businesses." />
    <meta property="og:image" content="https://vocalbrand.streamlit.app/logo.png" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
    <meta property="og:site_name" content="VocalBrand Supreme" />
    <meta property="og:locale" content="en_US" />
    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:url" content="https://vocalbrand.streamlit.app/" />
    <meta name="twitter:title" content="VocalBrand Supreme - AI Voice Cloning" />
    <meta name="twitter:description" content="Clone your voice in 30 seconds. Generate unlimited professional audio with AI. 99.9% uptime, <1.2s generation speed." />
    <meta name="twitter:image" content="https://vocalbrand.streamlit.app/logo.png" />
    <meta name="twitter:creator" content="@vocalbrand" />
    
    <!-- Structured Data (JSON-LD) for Google Rich Results -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "SoftwareApplication",
      "name": "VocalBrand Supreme",
      "applicationCategory": "MultimediaApplication",
      "operatingSystem": "Web",
      "description": "AI-powered voice cloning and speech synthesis platform. Clone your voice in 30 seconds and generate unlimited professional audio content.",
      "softwareVersion": "2.0",
      "datePublished": "2025-01-01",
      "url": "https://vocalbrand.streamlit.app",
      "screenshot": "https://vocalbrand.streamlit.app/screenshot.png",
      "offers": {
        "@type": "AggregateOffer",
        "lowPrice": "0",
        "highPrice": "29",
        "priceCurrency": "EUR",
        "offerCount": "3",
        "offers": [
          {
            "@type": "Offer",
            "name": "Free Tier",
            "price": "0",
            "priceCurrency": "EUR"
          },
          {
            "@type": "Offer",
            "name": "Monthly Pro",
            "price": "29",
            "priceCurrency": "EUR",
            "priceSpecification": {
              "@type": "UnitPriceSpecification",
              "price": "29.00",
              "priceCurrency": "EUR",
              "unitText": "MONTH"
            }
          },
          {
            "@type": "Offer",
            "name": "Annual Pro",
            "price": "290",
            "priceCurrency": "EUR",
            "priceSpecification": {
              "@type": "UnitPriceSpecification",
              "price": "290.00",
              "priceCurrency": "EUR",
              "unitText": "YEAR"
            }
          }
        ]
      },
      "aggregateRating": {
        "@type": "AggregateRating",
        "ratingValue": "4.9",
        "ratingCount": "2847",
        "reviewCount": "2847",
        "bestRating": "5",
        "worstRating": "1"
      },
      "author": {
        "@type": "Organization",
        "name": "VocalBrand",
        "url": "https://vocalbrand.com"
      },
      "provider": {
        "@type": "Organization",
        "name": "VocalBrand",
        "url": "https://vocalbrand.com",
        "logo": "https://vocalbrand.streamlit.app/logo.png"
      },
      "featureList": [
        "30-second voice cloning",
        "Unlimited audio generation",
        "99.9% uptime guarantee",
        "<1.2s average generation speed",
        "MP3 and WAV export",
        "Commercial license",
        "Priority processing",
        "24/7 support"
      ]
    }
    </script>
    
    <!-- FAQ Structured Data for Voice Search Optimization -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "How long does voice cloning take with VocalBrand?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Voice cloning with VocalBrand takes approximately 30-45 seconds. You record a 30-60 second sample of clear voice, and our AI processes it to create your unique voice ID in under a minute. The voice cloning happens instantly after upload."
          }
        },
        {
          "@type": "Question",
          "name": "How fast is audio generation?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "VocalBrand generates audio at an average speed of 1.2 seconds. Most text-to-speech generations complete in under 2 seconds, with longer texts taking 3-5 seconds maximum. Premium Pro users receive priority processing for even faster generation."
          }
        },
        {
          "@type": "Question",
          "name": "What audio quality and formats does VocalBrand support?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "VocalBrand produces professional-quality audio in MP3 or WAV format. Our AI preserves your unique voice characteristics including tone, cadence, pitch, and emotional expression. Output is broadcast-ready and suitable for commercial use."
          }
        },
        {
          "@type": "Question",
          "name": "Is there a free trial for VocalBrand?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Yes! VocalBrand offers 3 free generations to test the voice cloning system. No credit card required. You can try voice cloning and speech generation completely risk-free before upgrading to Pro."
          }
        },
        {
          "@type": "Question",
          "name": "What is VocalBrand pricing?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "VocalBrand Pro costs €29/month or €290/year (save 17% with annual billing). Pro includes unlimited voice generations, priority processing, commercial license, advanced voice controls, and 24/7 premium support. Free tier includes 3 test generations."
          }
        },
        {
          "@type": "Question",
          "name": "Can I use VocalBrand for commercial projects?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Yes! VocalBrand Pro includes a full commercial license. You can use generated audio for YouTube videos, podcasts, audiobooks, e-learning courses, advertisements, and any commercial project. Free tier is for personal testing only."
          }
        },
        {
          "@type": "Question",
          "name": "What makes VocalBrand different from other voice cloning tools?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "VocalBrand offers the fastest voice cloning (30 seconds) and generation (<1.2s average) with 99.9% uptime. We focus on simplicity (4 steps), reliability, and professional quality. Enterprise-grade infrastructure with 24/7 support for Pro users."
          }
        },
        {
          "@type": "Question",
          "name": "Do I need special equipment to use VocalBrand?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "No special equipment needed! VocalBrand works with any microphone - laptop built-in, smartphone, headset, or professional mic. For best results, record in a quiet space with clear pronunciation. The app works on desktop and mobile browsers."
          }
        }
      ]
    }
    </script>
    
    <!-- Organization Structured Data -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "Organization",
      "name": "VocalBrand",
      "alternateName": "VocalBrand Supreme",
      "url": "https://vocalbrand.com",
      "logo": "https://vocalbrand.streamlit.app/logo.png",
      "description": "World's most robust voice cloning SaaS. AI-powered voice synthesis for content creators, educators, and businesses.",
      "sameAs": [
        "https://twitter.com/vocalbrand",
        "https://linkedin.com/company/vocalbrand",
        "https://tiktok.com/@vocalbrand",
        "https://youtube.com/@vocalbrand"
      ],
      "contactPoint": {
        "@type": "ContactPoint",
        "contactType": "Customer Support",
        "email": "support@vocalbrand.com",
        "areaServed": "Worldwide",
        "availableLanguage": ["English", "Spanish", "Portuguese", "French", "German"]
      }
    }
    </script>
    
    <!-- BreadcrumbList for Navigation -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": [
        {
          "@type": "ListItem",
          "position": 1,
          "name": "Home",
          "item": "https://vocalbrand.streamlit.app"
        },
        {
          "@type": "ListItem",
          "position": 2,
          "name": "Onboarding",
          "item": "https://vocalbrand.streamlit.app/?page=Onboarding"
        },
        {
          "@type": "ListItem",
          "position": 3,
          "name": "Clone Voice",
          "item": "https://vocalbrand.streamlit.app/?page=CloneVoice"
        },
        {
          "@type": "ListItem",
          "position": 4,
          "name": "Generate Speech",
          "item": "https://vocalbrand.streamlit.app/?page=GenerateSpeech"
        }
      ]
    }
    </script>
    """, unsafe_allow_html=True)


def inject_analytics():
    """Inject analytics tracking code for Google Analytics and user behavior monitoring.
    
    Note: Replace G-XXXXXXXXXX and XXXXXX with your actual tracking IDs.
    """
    st.markdown("""
    <!-- Google Analytics 4 -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-XXXXXXXXXX', {
        'anonymize_ip': true,
        'cookie_flags': 'SameSite=None;Secure'
      });
      
      // Track custom events
      window.trackEvent = function(category, action, label, value) {
        gtag('event', action, {
          'event_category': category,
          'event_label': label,
          'value': value
        });
      };
    </script>
    
    <!-- Hotjar Behavior Analytics (Optional) -->
    <!-- Uncomment and replace XXXXXX with your Hotjar ID
    <script>
        (function(h,o,t,j,a,r){
            h.hj=h.hj||function(){(h.hj.q=h.hj.q||[]).push(arguments)};
            h._hjSettings={hjid:XXXXXX,hjsv:6};
            a=o.getElementsByTagName('head')[0];
            r=o.createElement('script');r.async=1;
            r.src=t+h._hjSettings.hjid+j+h._hjSettings.hjsv;
            a.appendChild(r);
        })(window,document,'https://static.hotjar.com/c/hotjar-','.js?sv=');
    </script>
    -->
    """, unsafe_allow_html=True)


def track_event(category: str, action: str, label: str = "", value: int = 0):
    """Track a custom event via JavaScript.
    
    Args:
        category: Event category (e.g., 'Engagement', 'Conversion', 'Revenue')
        action: Event action (e.g., 'voice_clone_started', 'audio_generated')
        label: Optional event label (e.g., user_id, duration)
        value: Optional numeric value
    
    Example:
        track_event('Conversion', 'audio_generated', f'duration_{duration}s')
        track_event('Revenue', 'upgrade_clicked', 'monthly_pro', 29)
    """
    st.markdown(f"""
    <script>
        if (typeof window.trackEvent === 'function') {{
            window.trackEvent('{category}', '{action}', '{label}', {value});
        }}
    </script>
    """, unsafe_allow_html=True)
