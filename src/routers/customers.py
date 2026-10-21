from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from src.auth import verify_api_key
from src.database import get_db
from src.models import Customer
from src.schemas import CustomerCreate, CustomerOut, CustomerUpdate

router = APIRouter(
    prefix="/customers",
    tags=["customers"],
    dependencies=[Depends(verify_api_key)],
)


@router.post("", response_model=CustomerOut, status_code=201)
def create_customer(data: CustomerCreate, db: Session = Depends(get_db)):
    if db.query(Customer).filter(Customer.email == data.email).first():
        raise HTTPException(status_code=409, detail="Email already exists")
    customer = Customer(**data.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.get("", response_model=List[CustomerOut])
def list_customers(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return (
        db.query(Customer)
        .order_by(Customer.id)
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/{customer_id}", response_model=CustomerOut)
def update_customer(customer_id: int, data: CustomerUpdate, db: Session = Depends(get_db)):
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    changes = data.model_dump(exclude_unset=True)
    new_email = changes.get("email")
    if new_email and new_email != customer.email:
        if db.query(Customer).filter(Customer.email == new_email).first():
            raise HTTPException(status_code=409, detail="Email already exists")
    for field, value in changes.items():
        setattr(customer, field, value)
    db.commit()
    db.refresh(customer)
    return customer


@router.delete("/{customer_id}", status_code=204)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(customer)
    db.commit()
    return Response(status_code=204)