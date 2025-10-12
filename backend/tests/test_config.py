"""
Test configuration and environment loading.
"""
import pytest
import os
from pathlib import Path
from app.core.config import settings, Settings


class TestConfiguration:
    """Test configuration loading and validation."""
    
    def test_settings_instance_exists(self):
        """Test that settings instance is created successfully."""
        assert settings is not None
        assert isinstance(settings, Settings)
    
    def test_required_environment_variables_loaded(self):
        """Test that required environment variables are loaded."""
        # These are marked as required in the Settings class with Field(...)
        assert settings.SECRET_KEY, "SECRET_KEY must be set and non-empty"
        assert settings.DATABASE_URL, "DATABASE_URL must be set and non-empty"
        
        # Verify SECRET_KEY meets minimum length requirement
        assert len(settings.SECRET_KEY) >= 32, "SECRET_KEY must be at least 32 characters"
    
    def test_optional_environment_variables_handling(self):
        """Test that optional environment variables are handled gracefully."""
        # These should not cause errors even if not set
        assert hasattr(settings, 'OPENAI_API_KEY')
        assert hasattr(settings, 'SUPABASE_SERVICE_ROLE_KEY')
        assert hasattr(settings, 'SENTRY_DSN')
    
    def test_default_values_applied(self):
        """Test that default values are applied correctly."""
        assert settings.APP_NAME == "AdCopySurge"
        assert settings.APP_VERSION == "1.0.0"
        assert settings.ALGORITHM == "HS256"
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 60
        assert settings.REDIS_URL == "redis://localhost:6379/0"
    
    def test_environment_specific_settings(self):
        """Test environment-specific configuration."""
        # Should have ENVIRONMENT setting
        assert hasattr(settings, 'ENVIRONMENT')
        assert settings.ENVIRONMENT in ['development', 'staging', 'production']
        
        # Debug should be False in production
        if settings.ENVIRONMENT == 'production':
            assert settings.DEBUG is False
    
    def test_cors_origins_parsing(self):
        """Test that CORS origins are parsed correctly."""
        assert hasattr(settings, 'CORS_ORIGINS')
        assert isinstance(settings.CORS_ORIGINS, list)
        assert len(settings.CORS_ORIGINS) > 0
    
    def test_allowed_hosts_parsing(self):
        """Test that allowed hosts are parsed correctly."""
        assert hasattr(settings, 'ALLOWED_HOSTS')
        assert isinstance(settings.ALLOWED_HOSTS, list)
        assert len(settings.ALLOWED_HOSTS) > 0
    
    def test_paddle_api_url_environment_based(self):
        """Test that Paddle API URL is set based on environment."""
        if settings.PADDLE_ENVIRONMENT == 'production':
            assert settings.PADDLE_API_URL == "https://vendors.paddle.com/api"
        else:
            assert settings.PADDLE_API_URL == "https://sandbox-vendors.paddle.com/api"
    
    def test_config_properties(self):
        """Test configuration helper properties."""
        if settings.ENVIRONMENT == 'production':
            assert settings.is_production is True
            assert settings.is_development is False
        else:
            assert settings.is_production is False
            if settings.ENVIRONMENT == 'development':
                assert settings.is_development is True


class TestEnvironmentLoading:
    """Test environment file loading and path resolution."""
    
    def test_env_file_path_resolution(self):
        """Test that .env file path is resolved correctly."""
        # The config module should be able to find the .env file
        from app.core.config import ENV_FILE
        
        assert ENV_FILE.exists(), f".env file not found at {ENV_FILE}"
        assert ENV_FILE.name == ".env"
        assert ENV_FILE.parent.name == "backend"
    
    def test_explicit_dotenv_loading(self):
        """Test that explicit dotenv loading works."""
        from app.core.config import load_dotenv, ENV_FILE
        
        # Save current environment
        original_secret = os.environ.get('SECRET_KEY')
        
        try:
            # Remove SECRET_KEY from environment
            if 'SECRET_KEY' in os.environ:
                del os.environ['SECRET_KEY']
            
            # Reload environment variables
            load_dotenv(dotenv_path=ENV_FILE, override=True)
            
            # Should now be loaded from .env file
            assert os.environ.get('SECRET_KEY'), "SECRET_KEY should be loaded from .env file"
            
        finally:
            # Restore original environment
            if original_secret:
                os.environ['SECRET_KEY'] = original_secret
    
    def test_settings_creation_from_scratch(self):
        """Test creating a fresh Settings instance."""
        # This tests that Settings can be instantiated even after module import
        fresh_settings = Settings()
        
        assert fresh_settings.SECRET_KEY
        assert fresh_settings.DATABASE_URL
        assert fresh_settings.SECRET_KEY == settings.SECRET_KEY
        assert fresh_settings.DATABASE_URL == settings.DATABASE_URL


class TestDeploymentReadiness:
    """Test deployment-specific configuration requirements."""
    
    def test_production_security_requirements(self):
        """Test production security requirements."""
        if settings.ENVIRONMENT == 'production':
            # Should have strong security settings
            assert not settings.DEBUG, "DEBUG must be False in production"
            assert len(settings.SECRET_KEY) >= 32, "Production SECRET_KEY must be strong"
            assert 'localhost' not in str(settings.DATABASE_URL), "Production should not use localhost DB"
    
    def test_gunicorn_compatibility(self):
        """Test that configuration is compatible with Gunicorn startup."""
        # Test that importing config doesn't fail under various conditions
        import importlib
        import sys
        
        # Test re-importing the config module (simulates Gunicorn worker startup)
        if 'app.core.config' in sys.modules:
            config_module = sys.modules['app.core.config']
            importlib.reload(config_module)
            
            # Should still have valid settings
            assert hasattr(config_module, 'settings')
            assert config_module.settings.SECRET_KEY
            assert config_module.settings.DATABASE_URL


if __name__ == "__main__":
    # Allow running this test file directly
    pytest.main([__file__, "-v"])
