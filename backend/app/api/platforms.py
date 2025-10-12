"""
Platform configuration API endpoints.

Provides platform-specific settings, character limits, and configuration
for frontend components to use when building ad copy forms.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.constants.platform_limits import (
    Platform,
    EmojiLevel, 
    HumanTone,
    PLATFORM_LIMITS,
    PLATFORM_CONFIG,
    get_platform_limit,
    get_platform_config,
    get_content_length_info,
    get_ai_parameters,
    get_emoji_guideline,
    get_tone_instruction
)

router = APIRouter(prefix="/platforms", tags=["platforms"])

class PlatformInfo(BaseModel):
    """Platform information response model"""
    platform: str
    character_limit: int
    recommended_length: int
    formality_level: int
    emoji_default: str
    tone_default: str
    audience_mindset: str
    typical_cta: List[str]
    optimization_tips: List[str]

class PlatformLimitsResponse(BaseModel):
    """Response model for all platform limits"""
    limits: Dict[str, int]
    platforms: List[str]
    default_platform: str

class EmojiConfigResponse(BaseModel):
    """Response model for emoji configuration"""
    levels: List[str]
    guidelines: Dict[str, str]
    default_level: str

class HumanToneConfigResponse(BaseModel):
    """Response model for human tone configuration"""
    tones: List[str]
    instructions: Dict[str, str]
    ai_parameters: Dict[str, Dict[str, float]]
    default_tone: str

@router.get("/limits", response_model=PlatformLimitsResponse)
async def get_platform_limits():
    """Get character limits for all supported platforms."""
    return PlatformLimitsResponse(
        limits=PLATFORM_LIMITS,
        platforms=list(PLATFORM_LIMITS.keys()),
        default_platform=Platform.FACEBOOK
    )

@router.get("/{platform}", response_model=PlatformInfo)
async def get_platform_info(platform: str):
    """Get detailed information for a specific platform."""
    
    if platform not in PLATFORM_LIMITS:
        raise HTTPException(
            status_code=404,
            detail=f"Platform '{platform}' not supported. Available platforms: {list(PLATFORM_LIMITS.keys())}"
        )
    
    config = get_platform_config(platform)
    length_info = get_content_length_info(platform)
    
    return PlatformInfo(
        platform=platform,
        character_limit=length_info["character_limit"],
        recommended_length=length_info["recommended_length"],
        formality_level=config.get("formality_level", 5),
        emoji_default=config.get("emoji_default", EmojiLevel.MODERATE),
        tone_default=config.get("recommended_tone", HumanTone.CONVERSATIONAL),
        audience_mindset=config.get("audience_mindset", "General audience"),
        typical_cta=config.get("typical_cta", ["Learn More"]),
        optimization_tips=config.get("optimization_tips", [])
    )

@router.get("/emoji/config", response_model=EmojiConfigResponse)
async def get_emoji_config():
    """Get emoji configuration options."""
    return EmojiConfigResponse(
        levels=[level.value for level in EmojiLevel],
        guidelines={
            level.value: get_emoji_guideline(level)
            for level in EmojiLevel
        },
        default_level=EmojiLevel.MODERATE
    )

@router.get("/tone/config", response_model=HumanToneConfigResponse)
async def get_human_tone_config():
    """Get human tone configuration options."""
    return HumanToneConfigResponse(
        tones=[tone.value for tone in HumanTone],
        instructions={
            tone.value: get_tone_instruction(tone)
            for tone in HumanTone
        },
        ai_parameters={
            tone.value: get_ai_parameters(tone)
            for tone in HumanTone
        },
        default_tone=HumanTone.CONVERSATIONAL
    )

@router.get("/validate/{platform}")
async def validate_platform_content(platform: str, content: str):
    """Validate if content meets platform requirements."""
    
    if platform not in PLATFORM_LIMITS:
        raise HTTPException(
            status_code=404,
            detail=f"Platform '{platform}' not supported."
        )
    
    limit = get_platform_limit(platform)
    content_length = len(content)
    is_valid = content_length <= limit
    
    return {
        "platform": platform,
        "content_length": content_length,
        "character_limit": limit,
        "is_valid": is_valid,
        "remaining_chars": limit - content_length,
        "over_limit_by": max(0, content_length - limit)
    }

@router.get("/")
async def list_all_platforms():
    """Get overview of all supported platforms."""
    platforms_overview = []
    
    for platform in Platform:
        config = get_platform_config(platform.value)
        length_info = get_content_length_info(platform.value)
        
        platforms_overview.append({
            "platform": platform.value,
            "name": platform.value.title(),
            "character_limit": length_info["character_limit"],
            "formality_level": config.get("formality_level", 5),
            "emoji_default": config.get("emoji_default", EmojiLevel.MODERATE),
            "tone_default": config.get("recommended_tone", HumanTone.CONVERSATIONAL),
            "audience_mindset": config.get("audience_mindset", "General audience")
        })
    
    return {
        "platforms": platforms_overview,
        "total_platforms": len(platforms_overview),
        "emoji_levels": [level.value for level in EmojiLevel],
        "human_tones": [tone.value for tone in HumanTone]
    }