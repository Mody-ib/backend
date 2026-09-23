from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

router = APIRouter()

# Database connection
DATABASE_URL = "mysql+pymysql://root:YOUR_PASSWORD@localhost/recipe"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# Recipe table
class Recipe(Base):
    __tablename__ = "Recipe"

    recipe_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    name = Column(String(255))
    instructions = Column(String(1000))
    servings = Column(Integer)
    prep_time = Column(Integer)


# Request model
class RecipeCreate(BaseModel):
    user_id: int
    name: str
    instructions: str
    servings: int
    prep_time: int


# Response model
class RecipeResponse(BaseModel):
    recipe_id: int
    user_id: int
    name: str
    instructions: str
    servings: int
    prep_time: int

    class Config:
        from_attributes = True


# GET all recipes
@router.get("/recipes", response_model=list[RecipeResponse])
def get_all_recipes():

    db = SessionLocal()

    try:
        return db.query(Recipe).all()
    finally:
        db.close()


# GET one recipe
@router.get("/recipes/{recipe_id}", response_model=RecipeResponse)
def get_recipe(recipe_id: int):

    db = SessionLocal()

    try:
        recipe = db.query(Recipe).filter(
            Recipe.recipe_id == recipe_id
        ).first()

        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found"
            )

        return recipe

    finally:
        db.close()


# POST - create recipe
@router.post(
    "/recipes",
    response_model=RecipeResponse,
    status_code=status.HTTP_201_CREATED
)
def create_recipe(recipe: RecipeCreate):

    db = SessionLocal()

    try:
        new_recipe = Recipe(
            user_id=recipe.user_id,
            name=recipe.name,
            instructions=recipe.instructions,
            servings=recipe.servings,
            prep_time=recipe.prep_time
        )

        db.add(new_recipe)
        db.commit()
        db.refresh(new_recipe)

        return new_recipe

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )

    finally:
        db.close()


# PUT - update recipe
@router.put(
    "/recipes/{recipe_id}",
    response_model=RecipeResponse
)
def update_recipe(
    recipe_id: int,
    recipe: RecipeCreate
):

    db = SessionLocal()

    try:
        existing_recipe = db.query(Recipe).filter(
            Recipe.recipe_id == recipe_id
        ).first()

        if not existing_recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found"
            )

        existing_recipe.user_id = recipe.user_id
        existing_recipe.name = recipe.name
        existing_recipe.instructions = recipe.instructions
        existing_recipe.servings = recipe.servings
        existing_recipe.prep_time = recipe.prep_time

        db.commit()
        db.refresh(existing_recipe)

        return existing_recipe

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )

    finally:
        db.close()


# DELETE - delete recipe
@router.delete("/recipes/{recipe_id}")
def delete_recipe(recipe_id: int):

    db = SessionLocal()

    try:
        recipe = db.query(Recipe).filter(
            Recipe.recipe_id == recipe_id
        ).first()

        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found"
            )

        db.delete(recipe)
        db.commit()

        return {
            "message": "Recipe deleted successfully"
        }

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )

    finally:
        db.close()
