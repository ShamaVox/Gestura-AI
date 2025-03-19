import h5py
import os
from typing import Union, List

def delete_hdf5_groups(hdf5_path: str, groups_to_delete: Union[str, List[str]], 
                       backup: bool = True):
    """
    Delete specified groups from an HDF5 file.
    
    :param hdf5_path: Path to the HDF5 file
    :param groups_to_delete: Single group name or list of group names to delete
    :param backup: Whether to create a backup of the original file before deletion
    """
    # Ensure groups_to_delete is a list
    if isinstance(groups_to_delete, str):
        groups_to_delete = [groups_to_delete]
    
    # Create backup if specified
    if backup:
        backup_path = hdf5_path.replace('.hdf5', '_backup.hdf5')
        os.system(f'cp {hdf5_path} {backup_path}')
        print(f"Backup created: {backup_path}")
    
    # Open the file in append mode
    with h5py.File(hdf5_path, 'a') as f:
        # Track deleted groups
        deleted_groups = []
        
        # Attempt to delete each specified group
        for group_name in groups_to_delete:
            try:
                if group_name in f:
                    del f[group_name]
                    deleted_groups.append(group_name)
                    print(f"Deleted group: {group_name}")
                else:
                    print(f"Group not found: {group_name}")
            except Exception as e:
                print(f"Error deleting group {group_name}: {e}")
    
    # Optional: Use h5repack to reclaim disk space (requires h5repack utility)
    os.system(f'h5repack {hdf5_path} {hdf5_path}_temp && mv {hdf5_path}_temp {hdf5_path}')
    
    return deleted_groups

def main():
    """
    Example usage of the delete_hdf5_groups function
    """
    # Example HDF5 file path (adjust as needed)
    hdf5_path = 'data/dataset/landmarks.hdf5'
    
    # Example: Delete a single group
    delete_hdf5_groups(hdf5_path, 'Hello how are you-C004C012_250304BY')
    
    # Example: Delete multiple groups
    # delete_hdf5_groups(hdf5_path, ['video1-sign1', 'video2-sign2'])
    
    print("Import and use delete_hdf5_groups function to delete HDF5 groups.")

if __name__ == '__main__':
    main() 