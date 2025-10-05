@router.post("/logout")
def logout(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout user and blacklist tokens"""
    try:
        # Blacklist the current access token
        TokenBlacklistService.add_token_to_blacklist(
            db=db,
            token=credentials.credentials,
            user_id=current_user.id,
            token_type="access"
        )
        
        # Log logout
        AuditService.log_action(
            db=db,
            action="logout",
            user_id=current_user.id,
            resource="auth",
            details={"email": current_user.email},
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            status="success"
        )
        
        logger.info(f"User {current_user.id} logged out successfully")
        
        return {
            "message": "Successfully logged out",
            "tokens_revoked": True
        }
        
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )
