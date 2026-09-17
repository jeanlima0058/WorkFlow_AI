from app.firebase_config import db


def test_conexao_firebase():
    colecao = db.collection("users").limit(1).stream()

    for documento in colecao:
        print("Documento encontrado:", documento.id)

    print("Conexão com o Firebase realizada com sucesso!")


if __name__ == "__main__":
    test_conexao_firebase()