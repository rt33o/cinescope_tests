#Modul_4\Cinescope\db_requester\models.py
# Модель для таблицы accounts_transaction_template
from sqlalchemy import Column, String, Integer, Float, Text, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from typing import Dict, Any

Base = declarative_base()

class AccountTransactionTemplate(Base):
    __tablename__ = 'accounts_transaction_template'
    user = Column(String, primary_key=True)
    balance = Column(Integer, nullable=False)