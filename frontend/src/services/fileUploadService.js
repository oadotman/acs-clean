// File upload service for white-label assets
const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml'];
const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
const MAX_LOGO_DIMENSIONS = { width: 1000, height: 1000 };

export class FileUploadService {
  // Validate file before upload
  static validateFile(file, type = 'image') {
    const errors = [];

    if (!file) {
      errors.push('No file selected');
      return { isValid: false, errors };
    }

    // Check file type
    if (type === 'image' && !ALLOWED_IMAGE_TYPES.includes(file.type)) {
      errors.push('File must be an image (JPEG, PNG, GIF, WebP, or SVG)');
    }

    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      errors.push(`File size must be less than ${MAX_FILE_SIZE / (1024 * 1024)}MB`);
    }

    // Basic file name validation
    if (file.name.length > 255) {
      errors.push('File name is too long');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  // Create file preview URL
  static createPreviewUrl(file) {
    if (!file) return null;
    return URL.createObjectURL(file);
  }

  // Clean up preview URL
  static cleanupPreviewUrl(url) {
    if (url && url.startsWith('blob:')) {
      URL.revokeObjectURL(url);
    }
  }

  // Compress/resize image if needed
  static async processImage(file, maxWidth = MAX_LOGO_DIMENSIONS.width, maxHeight = MAX_LOGO_DIMENSIONS.height, quality = 0.8) {
    return new Promise((resolve, reject) => {
      // For SVG files, return as-is since they're vector
      if (file.type === 'image/svg+xml') {
        resolve(file);
        return;
      }

      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const img = new Image();

      img.onload = () => {
        // Calculate new dimensions while maintaining aspect ratio
        let { width, height } = img;
        
        if (width > maxWidth || height > maxHeight) {
          const ratio = Math.min(maxWidth / width, maxHeight / height);
          width *= ratio;
          height *= ratio;
        }

        // Set canvas dimensions
        canvas.width = width;
        canvas.height = height;

        // Draw and compress image
        ctx.drawImage(img, 0, 0, width, height);

        canvas.toBlob(
          (blob) => {
            if (blob) {
              // Create new file from blob
              const processedFile = new File([blob], file.name, {
                type: file.type,
                lastModified: Date.now()
              });
              resolve(processedFile);
            } else {
              reject(new Error('Failed to process image'));
            }
          },
          file.type,
          quality
        );
      };

      img.onerror = () => reject(new Error('Failed to load image'));
      img.src = URL.createObjectURL(file);
    });
  }

  // Convert file to base64 data URL for storage
  static async fileToBase64(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = () => reject(new Error('Failed to read file'));
      reader.readAsDataURL(file);
    });
  }

  // Upload logo specifically (with processing)
  static async uploadLogo(file) {
    try {
      // Validate file
      const validation = this.validateFile(file, 'image');
      if (!validation.isValid) {
        throw new Error(validation.errors.join(', '));
      }

      // Process/compress image
      const processedFile = await this.processImage(file);

      // Convert to base64 for storage
      const base64 = await this.fileToBase64(processedFile);

      return {
        success: true,
        data: {
          file: processedFile,
          base64,
          url: this.createPreviewUrl(processedFile),
          originalName: file.name,
          processedSize: processedFile.size,
          processedType: processedFile.type
        }
      };
    } catch (error) {
      console.error('Logo upload error:', error);
      return {
        success: false,
        error: error.message || 'Failed to upload logo'
      };
    }
  }

  // Mock API upload (replace with actual API call)
  static async uploadToServer(file, type = 'logo') {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));

      // In real implementation, this would:
      // 1. Upload file to cloud storage (AWS S3, Cloudinary, etc.)
      // 2. Return permanent URL
      // 3. Save reference in database

      // For now, return mock data
      return {
        success: true,
        url: URL.createObjectURL(file), // This would be the permanent URL
        id: `file_${Date.now()}`,
        size: file.size,
        type: file.type,
        uploadedAt: new Date().toISOString()
      };
    } catch (error) {
      console.error('Server upload error:', error);
      return {
        success: false,
        error: error.message || 'Failed to upload to server'
      };
    }
  }

  // Get image dimensions
  static async getImageDimensions(file) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve({ width: img.naturalWidth, height: img.naturalHeight });
      img.onerror = () => reject(new Error('Failed to load image'));
      img.src = URL.createObjectURL(file);
    });
  }

  // Validate image dimensions
  static async validateImageDimensions(file, minWidth = 32, minHeight = 32, maxWidth = 2000, maxHeight = 2000) {
    try {
      const dimensions = await this.getImageDimensions(file);
      const errors = [];

      if (dimensions.width < minWidth || dimensions.height < minHeight) {
        errors.push(`Image must be at least ${minWidth}×${minHeight} pixels`);
      }

      if (dimensions.width > maxWidth || dimensions.height > maxHeight) {
        errors.push(`Image must be no larger than ${maxWidth}×${maxHeight} pixels`);
      }

      return {
        isValid: errors.length === 0,
        errors,
        dimensions
      };
    } catch (error) {
      return {
        isValid: false,
        errors: ['Failed to read image dimensions'],
        dimensions: null
      };
    }
  }

  // Generate thumbnail
  static async generateThumbnail(file, size = 64) {
    try {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const img = new Image();

      return new Promise((resolve, reject) => {
        img.onload = () => {
          canvas.width = size;
          canvas.height = size;

          // Calculate crop area to maintain square aspect ratio
          const { width, height } = img;
          const cropSize = Math.min(width, height);
          const x = (width - cropSize) / 2;
          const y = (height - cropSize) / 2;

          ctx.drawImage(img, x, y, cropSize, cropSize, 0, 0, size, size);

          canvas.toBlob((blob) => {
            if (blob) {
              resolve(URL.createObjectURL(blob));
            } else {
              reject(new Error('Failed to generate thumbnail'));
            }
          }, 'image/jpeg', 0.8);
        };

        img.onerror = () => reject(new Error('Failed to load image for thumbnail'));
        img.src = URL.createObjectURL(file);
      });
    } catch (error) {
      console.error('Thumbnail generation error:', error);
      throw error;
    }
  }
}

// Utility functions
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const getFileExtension = (filename) => {
  return filename.split('.').pop().toLowerCase();
};

export const isImageFile = (file) => {
  return ALLOWED_IMAGE_TYPES.includes(file.type);
};

export default FileUploadService;