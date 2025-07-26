from fastapi import APIRouter, Depends, HTTPException, Response
from app.services.database_service import DatabaseService
from app.api.dependencies import get_database_service

router = APIRouter()

@router.get("/{image_id}")
async def get_image(
    image_id: int,
    db_service: DatabaseService = Depends(get_database_service)
):
    """
    ## 🖼️ Lấy ảnh hóa đơn
    
    **Trả về ảnh hóa đơn theo ID:**
    
    ### Đầu vào:
    - **image_id**: ID của ảnh trong database
    
    ### Đầu ra:
    - Trả về file ảnh với content-type phù hợp
    """
    try:
        # Get image from database
        db_image = db_service.get_image(image_id)
        
        if not db_image:
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Return image with proper content type
        return Response(
            content=db_image.image_data,
            media_type=db_image.content_type,
            headers={
                "Content-Disposition": f"inline; filename={db_image.filename}"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve image: {str(e)}")