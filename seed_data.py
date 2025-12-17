#!/usr/bin/env python3
"""Seed initial data for ApoloCopilot"""
from database import SessionLocal
from models.gamification import Badge
from models.forum import ForumCategory
from models.shifts import Shift, ShiftType, ShiftSource
from datetime import datetime, timedelta

def seed_badges(db):
    """Create default badges"""
    if db.query(Badge).count() > 0:
        print("⏩ Badges already exist, skipping...")
        return

    print("🏅 Creating badges...")
    badges = [
        Badge(
            name="Novato",
            description="Bem-vindo ao ApoloCopilot!",
            badge_type="newcomer",
            icon="🌱",
            color="#46D160",
            points_required=0,
            order=1
        ),
        Badge(
            name="Verificado",
            description="Telefone e documentos verificados",
            badge_type="verified",
            icon="✅",
            color="#0079D3",
            points_required=10,
            order=2
        ),
        Badge(
            name="Confiável",
            description="Conquistou a confiança da comunidade",
            badge_type="trusted",
            icon="⭐",
            color="#FFD700",
            points_required=50,
            order=3
        ),
        Badge(
            name="Ajudante",
            description="Ajudou outros membros da comunidade",
            badge_type="helper",
            icon="🤝",
            color="#00CED1",
            points_required=100,
            order=4
        ),
        Badge(
            name="Especialista",
            description="Reconhecido como especialista na área",
            badge_type="expert",
            icon="🎓",
            color="#9370DB",
            points_required=250,
            order=5
        ),
        Badge(
            name="Veterano",
            description="Membro ativo há muito tempo",
            badge_type="veteran",
            icon="🏆",
            color="#FF4500",
            points_required=500,
            order=6
        ),
        Badge(
            name="Moderador",
            description="Moderador da comunidade",
            badge_type="moderator",
            icon="🛡️",
            color="#FF6B35",
            points_required=1000,
            order=7
        )
    ]

    for badge in badges:
        db.add(badge)

    db.commit()
    print(f"✅ Created {len(badges)} badges")


def seed_forum_categories(db):
    """Create forum categories"""
    if db.query(ForumCategory).count() > 0:
        print("⏩ Forum categories already exist, skipping...")
        return

    print("📋 Creating forum categories...")
    categories = [
        ForumCategory(
            name="Geral",
            description="Discussões gerais sobre a plataforma",
            slug="geral",
            icon="💬",
            order=1
        ),
        ForumCategory(
            name="Plantões",
            description="Oportunidades e dúvidas sobre plantões médicos",
            slug="plantoes",
            icon="🏥",
            order=2
        ),
        ForumCategory(
            name="Dúvidas Técnicas",
            description="Problemas técnicos e suporte",
            slug="duvidas-tecnicas",
            icon="❓",
            order=3
        ),
        ForumCategory(
            name="Sugestões",
            description="Sugestões de melhorias para a plataforma",
            slug="sugestoes",
            icon="💡",
            order=4
        ),
        ForumCategory(
            name="Anúncios",
            description="Anúncios e novidades",
            slug="anuncios",
            icon="📢",
            order=5
        ),
        ForumCategory(
            name="Networking",
            description="Conecte-se com outros profissionais",
            slug="networking",
            icon="🤝",
            order=6
        )
    ]

    for category in categories:
        db.add(category)

    db.commit()
    print(f"✅ Created {len(categories)} forum categories")


def seed_sample_shifts(db):
    """Create sample shift opportunities"""
    if db.query(Shift).count() > 0:
        print("⏩ Sample shifts already exist, skipping...")
        return

    print("🏥 Creating sample shift opportunities...")
    shifts = [
        Shift(
            title="Plantão Emergência - Hospital São Paulo",
            description="Plantão de 12 horas no setor de emergência. Experiência mínima de 2 anos.",
            shift_type=ShiftType.EMERGENCY.value,
            source=ShiftSource.MANUAL.value,
            hospital_name="Hospital São Paulo",
            city="São Paulo",
            state="SP",
            address="Av. Paulista, 1000",
            latitude=-23.5505,
            longitude=-46.6333,
            shift_date=datetime.utcnow() + timedelta(days=3),
            shift_duration_hours=12.0,
            pay_rate=200.0,
            total_pay=2400.0,
            specialty_required="Clínica Geral",
            experience_required="2+ anos",
            is_active=True,
            expires_at=datetime.utcnow() + timedelta(days=7)
        ),
        Shift(
            title="UTI - Hospital Albert Einstein",
            description="Plantão noturno na UTI. Preferência para especialistas em terapia intensiva.",
            shift_type=ShiftType.ICU.value,
            source=ShiftSource.MANUAL.value,
            hospital_name="Hospital Albert Einstein",
            city="São Paulo",
            state="SP",
            address="Av. Albert Einstein, 627",
            latitude=-23.5989,
            longitude=-46.7155,
            shift_date=datetime.utcnow() + timedelta(days=5),
            shift_duration_hours=12.0,
            pay_rate=250.0,
            total_pay=3000.0,
            specialty_required="Terapia Intensiva",
            experience_required="3+ anos",
            is_active=True,
            expires_at=datetime.utcnow() + timedelta(days=10)
        ),
        Shift(
            title="Plantão Pediatria - Hospital Infantil Sabará",
            description="Atendimento pediátrico geral. Ambiente acolhedor.",
            shift_type=ShiftType.PEDIATRICS.value,
            source=ShiftSource.MANUAL.value,
            hospital_name="Hospital Infantil Sabará",
            city="São Paulo",
            state="SP",
            address="Av. Angélica, 1968",
            latitude=-23.5440,
            longitude=-46.6568,
            shift_date=datetime.utcnow() + timedelta(days=7),
            shift_duration_hours=6.0,
            pay_rate=180.0,
            total_pay=1080.0,
            specialty_required="Pediatria",
            experience_required="1+ ano",
            is_active=True,
            expires_at=datetime.utcnow() + timedelta(days=14)
        ),
        Shift(
            title="Plantão Cirurgia - Hospital Sírio-Libanês",
            description="Apoio cirúrgico em procedimentos eletivos e emergenciais.",
            shift_type=ShiftType.SURGERY.value,
            source=ShiftSource.MANUAL.value,
            hospital_name="Hospital Sírio-Libanês",
            city="São Paulo",
            state="SP",
            address="R. Dona Adma Jafet, 91",
            latitude=-23.5697,
            longitude=-46.6598,
            shift_date=datetime.utcnow() + timedelta(days=2),
            shift_duration_hours=8.0,
            pay_rate=300.0,
            total_pay=2400.0,
            specialty_required="Cirurgia Geral",
            experience_required="5+ anos",
            is_active=True,
            expires_at=datetime.utcnow() + timedelta(days=5)
        )
    ]

    for shift in shifts:
        db.add(shift)

    db.commit()
    print(f"✅ Created {len(shifts)} sample shifts")


def main():
    """Main seed function"""
    print("🌱 Seeding database with initial data...")
    print("=" * 50)

    db = SessionLocal()
    try:
        seed_badges(db)
        seed_forum_categories(db)
        seed_sample_shifts(db)

        print("=" * 50)
        print("✅ Database seeded successfully!")
        print()
        print("📊 Summary:")
        print(f"   Badges: {db.query(Badge).count()}")
        print(f"   Forum Categories: {db.query(ForumCategory).count()}")
        print(f"   Sample Shifts: {db.query(Shift).count()}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
