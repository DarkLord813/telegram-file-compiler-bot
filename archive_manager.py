import os
import zipfile
import py7zr
import tarfile
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class ArchiveManager:
    """Manages compilation and extraction of various archive formats"""
    
    @staticmethod
    async def compile_archive(files: List[Dict], output_path: str, format_type: str) -> bool:
        """Compile files into specified archive format"""
        try:
            if format_type == "zip":
                return ArchiveManager._create_zip(files, output_path)
            elif format_type == "7z":
                return ArchiveManager._create_7z(files, output_path)
            elif format_type == "tar":
                return ArchiveManager._create_tar(files, output_path)
            elif format_type == "tar.gz":
                return ArchiveManager._create_tar_gz(files, output_path)
            else:
                logger.error(f"Unsupported archive format: {format_type}")
                return False
        except Exception as e:
            logger.error(f"Error creating {format_type} archive: {e}")
            return False
    
    @staticmethod
    def _create_zip(files: List[Dict], output_path: str) -> bool:
        """Create ZIP archive"""
        try:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_info in files:
                    zipf.write(file_info['path'], file_info['name'])
            return True
        except Exception as e:
            logger.error(f"Error creating ZIP: {e}")
            return False
    
    @staticmethod
    def _create_7z(files: List[Dict], output_path: str) -> bool:
        """Create 7Z archive"""
        try:
            with py7zr.SevenZipFile(output_path, 'w') as sevenzf:
                for file_info in files:
                    sevenzf.write(file_info['path'], file_info['name'])
            return True
        except Exception as e:
            logger.error(f"Error creating 7Z: {e}")
            return False
    
    @staticmethod
    def _create_tar(files: List[Dict], output_path: str) -> bool:
        """Create TAR archive"""
        try:
            with tarfile.open(output_path, 'w') as tar:
                for file_info in files:
                    tar.add(file_info['path'], arcname=file_info['name'])
            return True
        except Exception as e:
            logger.error(f"Error creating TAR: {e}")
            return False
    
    @staticmethod
    def _create_tar_gz(files: List[Dict], output_path: str) -> bool:
        """Create TAR.GZ archive"""
        try:
            with tarfile.open(output_path, 'w:gz') as tar:
                for file_info in files:
                    tar.add(file_info['path'], arcname=file_info['name'])
            return True
        except Exception as e:
            logger.error(f"Error creating TAR.GZ: {e}")
            return False
    
    @staticmethod
    async def extract_archive(archive_path: str, extract_dir: str) -> List[Dict]:
        """Extract files from various archive formats"""
        try:
            extracted_files = []
            
            if archive_path.endswith('.zip'):
                extracted_files = ArchiveManager._extract_zip(archive_path, extract_dir)
            elif archive_path.endswith('.7z'):
                extracted_files = ArchiveManager._extract_7z(archive_path, extract_dir)
            elif archive_path.endswith('.tar'):
                extracted_files = ArchiveManager._extract_tar(archive_path, extract_dir)
            elif archive_path.endswith('.tar.gz') or archive_path.endswith('.tgz'):
                extracted_files = ArchiveManager._extract_tar_gz(archive_path, extract_dir)
            elif archive_path.endswith('.apk'):
                # APK is basically a ZIP file
                extracted_files = ArchiveManager._extract_zip(archive_path, extract_dir)
            else:
                logger.error(f"Unsupported archive format: {archive_path}")
                return []
            
            return extracted_files
        except Exception as e:
            logger.error(f"Error extracting archive: {e}")
            return []
    
    @staticmethod
    def _extract_zip(archive_path: str, extract_dir: str) -> List[Dict]:
        """Extract ZIP archive"""
        extracted_files = []
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            zipf.extractall(extract_dir)
            for file_info in zipf.infolist():
                if not file_info.is_dir():
                    file_path = os.path.join(extract_dir, file_info.filename)
                    extracted_files.append({
                        'name': file_info.filename,
                        'path': file_path,
                        'size': file_info.file_size
                    })
        return extracted_files
    
    @staticmethod
    def _extract_7z(archive_path: str, extract_dir: str) -> List[Dict]:
        """Extract 7Z archive"""
        extracted_files = []
        with py7zr.SevenZipFile(archive_path, 'r') as sevenzf:
            sevenzf.extractall(extract_dir)
            for file_info in sevenzf.list():
                if not file_info.is_directory:
                    file_path = os.path.join(extract_dir, file_info.filename)
                    extracted_files.append({
                        'name': file_info.filename,
                        'path': file_path,
                        'size': file_info.compressed
                    })
        return extracted_files
    
    @staticmethod
    def _extract_tar(archive_path: str, extract_dir: str) -> List[Dict]:
        """Extract TAR archive"""
        extracted_files = []
        with tarfile.open(archive_path, 'r') as tar:
            tar.extractall(extract_dir)
            for member in tar.getmembers():
                if member.isfile():
                    file_path = os.path.join(extract_dir, member.name)
                    extracted_files.append({
                        'name': member.name,
                        'path': file_path,
                        'size': member.size
                    })
        return extracted_files
    
    @staticmethod
    def _extract_tar_gz(archive_path: str, extract_dir: str) -> List[Dict]:
        """Extract TAR.GZ archive"""
        return ArchiveManager._extract_tar(archive_path, extract_dir)
    
    @staticmethod
    def get_supported_formats() -> Dict[str, str]:
        """Get supported archive formats with descriptions"""
        return {
            'zip': 'ZIP Archive (Universal)',
            '7z': '7-Zip Archive (High Compression)',
            'tar': 'TAR Archive (Unix)',
            'tar.gz': 'GZipped TAR Archive'
        }
    
    @staticmethod
    def is_archive_file(filename: str) -> bool:
        """Check if file is a supported archive format"""
        archive_extensions = {
            '.zip', '.7z', '.tar', '.tar.gz', '.tgz', 
            '.rar', '.apk', '.jar', '.war', '.ear'
        }
        return any(filename.lower().endswith(ext) for ext in archive_extensions)
    
    @staticmethod
    def can_extract_archive(filename: str) -> bool:
        """Check if we can extract this archive format"""
        extractable_extensions = {
            '.zip', '.7z', '.tar', '.tar.gz', '.tgz', '.apk'
        }
        return any(filename.lower().endswith(ext) for ext in extractable_extensions)
