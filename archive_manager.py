import os
import asyncio
from patoolib import extract_archive, test_archive
import py7zr
import zipfile
import tarfile

class ArchiveManager:
    @staticmethod
    def get_supported_formats():
        """Get supported archive formats for creation"""
        return {
            'zip': 'ZIP Archive',
            '7z': '7-Zip Archive',
            'tar': 'TAR Archive',
            'tar.gz': 'GZipped TAR'
        }
    
    @staticmethod
    def can_extract_archive(filename):
        """Check if file can be extracted"""
        extractable_extensions = {'.apk', '.zip', '.7z', '.tar', '.gz', '.tar.gz', '.rar'}
        file_ext = os.path.splitext(filename.lower())[1]
        return file_ext in extractable_extensions
    
    @staticmethod
    def is_archive_file(filename):
        """Check if file is an archive"""
        archive_extensions = {'.zip', '.7z', '.tar', '.gz', '.tar.gz', '.rar', '.apk'}
        file_ext = os.path.splitext(filename.lower())[1]
        return file_ext in archive_extensions
    
    @staticmethod
    async def compile_archive(files, output_path, format_type):
        """Compile files into an archive"""
        try:
            if format_type == 'zip':
                return await ArchiveManager._create_zip(files, output_path)
            elif format_type == '7z':
                return await ArchiveManager._create_7z(files, output_path)
            elif format_type == 'tar':
                return await ArchiveManager._create_tar(files, output_path)
            elif format_type == 'tar.gz':
                return await ArchiveManager._create_tar_gz(files, output_path)
            else:
                return False
        except Exception as e:
            print(f"Error creating archive: {e}")
            return False
    
    @staticmethod
    async def _create_zip(files, output_path):
        """Create ZIP archive"""
        try:
            with zipfile.ZipFile(output_path, 'w') as zipf:
                for file_info in files:
                    arcname = os.path.basename(file_info['path'])
                    zipf.write(file_info['path'], arcname)
            return True
        except Exception as e:
            print(f"Error creating ZIP: {e}")
            return False
    
    @staticmethod
    async def _create_7z(files, output_path):
        """Create 7Z archive"""
        try:
            with py7zr.SevenZipFile(output_path, 'w') as archive:
                for file_info in files:
                    archive.write(file_info['path'], os.path.basename(file_info['path']))
            return True
        except Exception as e:
            print(f"Error creating 7Z: {e}")
            return False
    
    @staticmethod
    async def _create_tar(files, output_path):
        """Create TAR archive"""
        try:
            with tarfile.open(output_path, 'w') as tar:
                for file_info in files:
                    tar.add(file_info['path'], arcname=os.path.basename(file_info['path']))
            return True
        except Exception as e:
            print(f"Error creating TAR: {e}")
            return False
    
    @staticmethod
    async def _create_tar_gz(files, output_path):
        """Create TAR.GZ archive"""
        try:
            with tarfile.open(output_path, 'w:gz') as tar:
                for file_info in files:
                    tar.add(file_info['path'], arcname=os.path.basename(file_info['path']))
            return True
        except Exception as e:
            print(f"Error creating TAR.GZ: {e}")
            return False
    
    @staticmethod
    async def extract_archive(archive_path, extract_dir):
        """Extract archive files"""
        try:
            if archive_path.lower().endswith('.7z'):
                return await ArchiveManager._extract_7z(archive_path, extract_dir)
            else:
                return await ArchiveManager._extract_generic(archive_path, extract_dir)
        except Exception as e:
            print(f"Error extracting archive: {e}")
            return []
    
    @staticmethod
    async def _extract_7z(archive_path, extract_dir):
        """Extract 7Z archive"""
        try:
            with py7zr.SevenZipFile(archive_path, 'r') as archive:
                archive.extractall(extract_dir)
            
            # Get list of extracted files
            extracted_files = []
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    extracted_files.append({
                        'name': file,
                        'path': file_path,
                        'size': os.path.getsize(file_path)
                    })
            
            return extracted_files
        except Exception as e:
            print(f"Error extracting 7Z: {e}")
            return []
    
    @staticmethod
    async def _extract_generic(archive_path, extract_dir):
        """Extract generic archive using patool"""
        try:
            extract_archive(archive_path, outdir=extract_dir)
            
            # Get list of extracted files
            extracted_files = []
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    extracted_files.append({
                        'name': file,
                        'path': file_path,
                        'size': os.path.getsize(file_path)
                    })
            
            return extracted_files
        except Exception as e:
            print(f"Error extracting generic archive: {e}")
            return []
