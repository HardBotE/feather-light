from fastapi import APIRouter

document_router=APIRouter(prefix='/api/document/{document_id}')

@document_router.get('/')
def download_document():
    pass

@document_router.patch('/')
def update_document():
    pass

@document_router.delete('/')
def delete_document():
    pass


